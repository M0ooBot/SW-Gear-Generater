r"""W8's, W7's, W6's, W5's (and W4's) Windows demonstration: gearbox workbooks through the app's own code, on real SolidWorks and Excel.

python.exe probe/workbook_assembly_check.py <repo src> <output folder under C:\> --pid PID [--log FILE]
                                            [--only s0|s1|p1|…|p7|r1|…|r8|m1|…|m8|a|a2|a3|b|c|rs1|rs2|rs3
                                                    |modes|planetary|confirm7|w6|confirm|ring ...]
                                            [--fixtures FOLDER]
                                            [--m4-offset MM]

PLAN-WORKBOOK §6; W4 "Demonstrable" and the W4 decisions' item 10; W5-PLAN §4 with W5-DECISIONS' rulings; W6-PLAN §6
with W6-INTERFACES §4 and §7.17. Every
step goes the way the Workbook window goes (``workbook_gui.WorkbookWindow``: ``_plan_solidworks_pass``,
``_start_build`` with its journal, ``press_update``, ``_build_again``, ``_finish_build``, ``_finish_update``,
``_collect_job``), with the window's Tk thread played by this script's main thread and its worker by
``swcom.Worker``: the workbook read by ``link.Link.read`` / ``Link.poll``, ``assess``, ``plan_gearbox`` or
``classify``, ``swbuild.build_gearbox(session, **plan.build_kwargs())`` or
``swbuild.update_gearbox(session, **update.update_kwargs())``, then ``finish_build`` / ``finish_update`` with the
sidecars and the record written through ``store.save`` and ``store.save_link_record``. Every sentence the footer
would show is logged (``ui_text.workbook_footer`` with the read's digest, ``gearbox_status`` with ``again``,
``gearbox_update_status`` with the finish, ``job_failed`` for a refusal, ``build_again_question``). Every edit to
a workbook is made by a real Excel saving the file: an Excel this script starts for itself
(``probe/excel/xlhelp.Excel``), never the user's, quit at the end.

Nothing is taken on the app's word: each assembly is measured.

- §4.1, every build: each gear component's live frame (``Transform2``) against ``layout.frames`` of the current
  read to 1e-6 — exactly for a gearbox built to turn (as built or put, its gears stand at the built turn), modulo
  the gear's pitch for W4's static one; the layout component at identity. Each layout axis by
  ``GetRefAxisParams``: where it crosses z = 0 and that it reads +Z. Interference: none. The mates in the
  assembly exactly the record's names, nothing else in the mate group, every error code 0, none suppressed, every
  mated gear ``GetConstrainedStatus`` 2 (``findings.COMPONENT_UNDER_DEFINED``). For every listed mesh a negative
  control: one of its gears turned half its pitch about its own axis (a put with the gear mate on,
  ``findings.MESH_PHASE_ROUTE``) must interfere, and only with its partner; put back, none again — the gear
  turned is one in no lock, or, when both are (Risky_Placements' G3–G4), every lock touching either is suppressed
  around the put and turned back on after; then the frames and the mates are read again. Saved, closed, reopened,
  every document unmodified straight after the open, the frames and the mates the same.
- §4.2, the driven proof (the script's own, never the app's): a temporary angle mate from the input anchor's Top
  plane (``gearN:plane2``) to the layout's Right plane (``layout:plane3``) at 90°, its D1 linked to an assembly
  global "Drive"; "Drive" 90 -> 120 and a top-only rebuild; each gear's turn about its own +Z
  (``swbuild.turn_between``) against the kinematics, δ_i = 30° · ω_i / ω_in with ``kinematics.solve``'s speeds
  about each shaft's own axis (W5-DECISIONS M2), to 1e-6 relative, sign included. The wrong-sense control: the
  section's chosen gear mate suppressed and a temporary one made in its place with the other Flip; driven again,
  the comparison must SEE its gear b turning the wrong way. Then, as review M12 rules: "Drive" set back to 90 before
  the control mate is deleted; the control mate deleted and the recorded one turned back on; the drive's link and
  global (``delete_equation``) and the angle mate deleted; every frame against the built frames to 1e-6; and,
  before anything is saved, no "Drive" equation, no angle or control mate left, no mate suppressed. If the 90°
  drive moves a gear when it is added, or turns the input other than findings.DEMONSTRATION_DRIVE_SENSE says, the
  whole run STOPS (W5-PLAN §4.2: stop and ask).
- The marks: SolidWorks' ``GetSaveFlag`` after a build (no part and no layout part, and the assembly) and after
  every Update (``GearboxUpdate.changed``, and the assembly when it was rebuilt). Where SolidWorks marks MORE than
  that it is a NOTE (logged, listed at the end, not a failure) for the coordinator to rule on; a document expected
  marked and not marked is a FAIL.

W6 (W6-PLAN §6.1; the fixtures of §5 written by ``write_new`` with the Output folder blank, saved once by Excel, read
with the section's folder as the strip's). On top of §4.1 and §4.2: frames against ``layout.frames`` for any axis;
each layout axis (``GetRefAxisParams``) on its shaft's line to 1e-6 mm, either way along it, the sign logged; the
drive mates the input's Top plane to the layout's base plane square to the input's u₀ (Right for a Z or Y input, Top
for an X input), and the input's turn is MEASURED (|δ_in| = 30° asserted; a Z+ input must also turn as
findings.DEMONSTRATION_DRIVE_SENSE says), every other gear judged as δ_in · ω_i / ω_in; every gear mate's read
(Reverse, both entity directions and points, the gear each lies along and its τ — only τa·τb on parallel axes —
rule H's verdict and the app's own) logged after the build, after each Flip of a control (and held against the
drive's verdict) and after a reopen; after every control drive the interference read at the driven position, and on
a turned mesh judged (review M2): the Flip the drive calls right clear, the other clashing with the mesh's partner
alone — a failure STOPS the run; a quiet Update (W6-INTERFACES §7.17 (b)) on every built turned gearbox, every
document's GetSaveFlag read before and after and every frame unchanged. Nothing about which Flip is right is assumed
on SolidWorks 2024 (§7.17 (c)): it is logged, and the app's read and the drive must agree.

- ``r1``: fixture A, Bevel_Reducer, built fresh: the Checks panel, header, speeds and torques of §5.1 and §5's drive
  turns held against the app before the build; built turning; §4.1 (half-pitch controls on both meshes); the drive
  with both Flips on G1 meshes G2; a quiet Update; reopen, read, drive with both Flips again. Then the folder ends
  clean and is renamed ``r1.master`` (copy_built step 1, once).
- ``r5``: fixture B, Crossed_Slant, likewise (the slanted axis on its line; both Flips on G1 meshes G2, skew at 90°,
  and on G3 meshes G4, meeting at 120°); kept as ``r5.master``.
- ``r2`` (a copy of r1.master): the user's turn (37°) and Update with nothing changed; Excel S1 Z 60 -> 64 and G2 At
  60 -> 64 -> Update: "S1 Z" and "G2 Apex Z" read 64, every gear put, frames, the cone tips together in SolidWorks,
  the half-pitch controls, the drive, reopen.
- ``r3`` (a copy of r1.master): G1 Teeth 20 -> 21 -> Update remakes the turned gear mate G1 meshes G2 at 21 : 40, read
  back (§7.17 (a)): the marks, "Mate Teeth" read from both parts, every read, frames, mates, interference, the
  controls, the drive at 21 : 40 with both Flips and the interference judge, a quiet Update, reopen, drive.
- ``r4`` (a copy of r1.master): S1 Axis X+ -> X- -> the structural sentence; Build again… makes Bevel_Reducer_r2
  beside the earlier files (sha256 and mtime unchanged); §4.1; the drive, both Flips on G1 meshes G2.
- ``r6`` (a copy of r5.master): G1 At 10 -> 11 by Update ("G1 Face Z" 3); G4 Teeth 30 -> 31 by Update (the 120° gear
  mate remade, as r3); S3's Axis changed -> classify only, the slanted structural sentence. Then review M4's sense
  change on the classify path: fixture B's crossed stage alone, 10 mm up (folder r6-sense), built; S1 moved to the
  other side of S2 -> ``resensed`` names G1 meshes G2, the plan's k the record's negated; nothing pressed.
- ``r8`` (a copy of r5.master): the crossed stage's teeth 20/40 -> 21/39 (the centre distance kept) by Update: the skew
  gear mate remade at 21 : 39 and read back, as r3 (§7.17 (a) on fixture B's crossed stage).
- ``r7``: fixture A turned onto a Y input (Bevel_Reducer_Y): G1's cone tip at -30 along Y, an along mate to the Top
  plane with a negative coordinate (fixture B's G2 gives the Right plane's: "G2 Face X" -8); frames against the plan,
  the drive from the Right plane, both Flips on G1 meshes G2.

A copy section starts from ``copy_built(<builder>.master, section)`` (W6-INTERFACES §4, pinned): the master's folder
copied with its mtimes, every path in its records and sidecars put onto the copy through ``store``'s reader and
writer (only where the original folder is followed by a separator), the record asserted ours, whole, nothing
dropped by clear_saved, its digest the read's; then the copy's assembly opened once (the run's first copy under the
dialog watch with a 120 s timeout, W6-PLAN §7.1: a dialog drops the copy route), every component and the layout found
in the copy, closed without saving. Any step that fails is said and the section builds its fixture fresh, as it does
when no master exists in the run (``--only r3`` alone). Each copy section ends clean (step 4).
``--only w6`` runs r1 r5 r2 r3 r4 r6 r8 r7; ``--only confirm`` runs SolidWorks 2024's confirming set, r1 r5 r3 r6 r8
m3.

W7 (W7-PLAN §6; ``--only planetary`` runs p1–p7, ``--only confirm7`` SolidWorks 2024's p1 and p5). On a planetary
everything above holds, with: each carrier measured as a body (its frame, its constrained status 2, IsFixed when
held); the carrier part read as a skeleton (no solid body, no solid feature) and its axes carried into the assembly
by the carrier component's frame, each copy's axis through that copy's centre; each copy (and the sun) turned half a
pitch must clash with exactly its partners; the drive judged body by body against ``expected_frames`` (each copy's
origin carried round its carrier: the spike's (17.846008, 2.349471) …), every listed mesh at copy level in step by
its own carrier-frame relation, the unmated ring meshes included, no interference with the Drive at 120 nor at
phases across the input's pitch; a control's right Flip is the one whose whole train turns as the kinematics say,
the wrong one must clash; ``same_sense`` and the record's sense in the carrier's frame. A failure there logs FAIL
and the run goes on (no halt).

- ``p1``: Planetary_4to1 (§4.1) built fresh: the read against §4.1 (no diagnostic, the header, speeds, the planet on
  its carrier, torques and the held ring's, the Speeds lines), the gear mates (one per sun mesh, one with the ring)
  and the unmated ring meshes, every read, §4.1's checks, the drive with both Flips on Planet copy 1 meshes Ring and
  on Sun meshes Planet copy 2 (CarrierGear turning with the carrier), a quiet Update, reopen, drive; kept as
  ``p1.master``.
- ``p2`` (copy): the user's turn (37°) and Update with nothing changed; then, never saved, a second planet–ring gear
  mate made with each Flip and deleted, what SolidWorks answers logged as facts.
- ``p3`` (copy): before each edit the train driven 37° and left turned; (1) Planet At 12 (the carrier put first),
  (2) Ring At 12 (the held ring first, then the carrier), (3) Sun 21, Ring 57, P's X 19.5: the carrier part's
  globals, all four gear mates remade and read back, the drive at 3.714 : 1 with both Flips, a quiet Update, reopen.
- ``p4`` (copy): Copies 5 and 6 refused; Copies 4 -> Build again… with four copies of one part.
- ``p5``, ``p6``, ``p7`` (copies): the sun held (the drive from the ring), the stage on Z- (the carrier part's own
  coordinates p1's), the carrier held (it and CarrierGear fixed and never mated) -> Build again… each, measured,
  driven with both Flips on the ring mate, reopened, driven.

W8 (W8-PLAN §5; ``--only modes`` runs s0 to s4, the sections written so far: s5–s7 are a later stage's). The fixtures
are ``tests/workbook_fixtures.py``'s two (W8-PLAN §2), written by ``write_new`` with the Output folder blank and saved
once by Excel, as W6's are. Each mode is a configuration; every SolidWorks job of these sections opens the assembly,
shows the mode it works in and rebuilds before it finds any component, so no component or mate handle is held across
a configuration change (§1.8's handle rule). On top of W5's every-build checks:

- the read against §2.3 before the build: no error, the four modes, what each engages, where each slider stands and
  its face span, each mode's speeds (a free shaft has none) and ratio, and the kinematics against §2.3's 30° row for
  every body in every mode;
- the plan's configurations (each coupling made in the first mode it is on in, every slide's value per mode); the
  build's own per-mode checks (``GearboxResult.modes``: values, flags, no interference in any mode); the record
  (schema 6: the modes, each slide's values, each coupling's on-set, ratio 1 : 1 and sense −1, every component's
  frame per mode);
- every mode measured (``measure_modes``): shown nothing, the configurations exactly the modes and the first active,
  every mate's flag and every slide's value in every configuration against the record; then each mode shown and
  rebuilt: every body at its frame on record for the mode to 1e-6, each slider's origin at its slide's value, the
  mates exactly the record's, the per-mode mates off there suppressed and every other on with code 0, every mated
  body under-defined, the layout and every fixed body IsFixed through fresh handles, no interference; a half-pitch
  control on every dog (the dog put 6° with every lock touching it suppressed in that mode only: clashes with its
  sleeve alone where the mode engages it, with nothing where it does not, and the bodies the put moved besides it
  logged); in every mode W5's and W7's half-pitch controls on the listed meshes (review S1: N engages nothing); every
  mode shown again after the controls and its frames read. Every expectation of flags, values, the mates off in a
  mode and the drive's turns is §2.3's key itself (review S3, S4), the record held to the key separately; after the
  build a raw ``IsSuppressed2(3, GetConfigurationNames())`` of every coupling and one slide, paired in document order,
  beside the app's per-name read (run 1 found it answers in document order), and one with the names reversed;
- the driven proof in every mode (``mode_drive_proof``; W5's angle-mate drive with the mode shown — when SolidWorks
  refuses the drive's link to its global with several configurations, as the W8 spike saw Add2 do, "Drive" is the
  angle mate's own value in that mode): every body's turn against the mode's kinematics to 1e-6 relative, sleeves and
  dogs included, a body free in the mode standing still (one that turns is a NOTE); copies carried round; every
  mesh, engaged coupling and the spline in step; no interference at 120; the both-Flips control on the spline
  ``ModeSlv splined to RangeSlv`` in 4H and on ``RangeSlv engages LoDog`` in 4L — exactly one Flip turns every body
  right and the app's read names it, else the run HALTS (W8-PLAN §0.5); then M12's hygiene and every flag in every
  configuration as recorded;
- reopened: saved in the first mode, every document unmodified straight after the open and the first mode active;
  every mode measured again (no controls); the first mode shown and rebuilt last (review S2).

A failure that is one of W8-PLAN §0.5's STOP triggers is a FAIL followed by a ``STOP`` line, and is listed again at
the end; the section goes on gathering. Among them (review S5): a window that comes up while a configuration call
(or a save or open after the run made a configuration) is in progress — every ``call`` is traced for the dialog
watcher — unless it is the box already seen before any configuration was made (SolidWorks' startup notification, a
NOTE); a frame reading None; a gear mate the build reads wrong both ways round. s1 is kept as ``s1.master`` only with
no FAIL and no STOP of its own (review S6); a later section that copies it checks ``s_blocked``.

- ``s0``: TransferCase_Parallel (§2.2), the shakedown, W7-free: built fresh and judged as above.
- ``s1``: the E4 transfer case (§2.1): E3's 4 : 1 planetary as the low range; built fresh (the one E4 build), judged as
  above with W7's carrier part read as a skeleton; then kept as ``s1.master`` for ``copy_built``.

s2, s3 and s4 each start from ``copy_built`` of ``s1.master`` in the run's output folder (``start_w8_copy``: a copy
that asks anything or resolves outside the copy is a STOP, never a fresh build). Every Update is pressed with its
SolidWorks calls traced (``w8_update``: shows, flags, values, rebuilds, puts, mates made), so what it showed, set and
put, and in what order, is read from the calls, and its elapsed time logged. Expectations are §2.3's key as each
section's own workbook edit changes it (``KEY``), and frames after an Update the built ones moved by the edit.

- ``s2`` (as the running version answers ``swcom.positions_per_configuration``): the user's turn in 2H (37°); 4H, N
  and 4L shown — False: each at 2H's turn from its own frames, 4L's LoDog across RangeSlv; True: each as built — and
  2H at the turn; Update in 4L — False: 4L's couplings found across and every mode put whole to the built frames, 4L
  last, each read from frames after the press, the call trace and the sentences' finding-free parts checked; True:
  quiet — then a fresh turn in 2H (the modes put in before it logged) and Update in 2H: nothing put or shown, False's
  sentence on a turn shown in every mode; 4L shown and read as a fact; Update in 4L judged by what it reports; FDrive, FIdler and FOut At 130 -> 132 -> Update: every mode put, 4L last, the
  carrier first in each; raw flags of every mate straight after; the globals; every mode measured with every
  control; the drive in 4H and 4L.
- ``s3``: in 4L RangeSlv engages LoDog suppressed and RangeSlv engages InDog on, N's slide at 58 -> Update in 2H puts
  them right before showing anything, then shows every mode; measured; an angle mate the record does not know (on the
  Sun, 2H active): on in every mode, then in N only -> refused naming the modes, nothing shown, set or put before the
  refusal, the mate read once per mode; suppressed everywhere -> listed and left; Exploded added -> listed and left,
  then active (the mate on in N meanwhile) -> J13's refusal, the mate never read; 4H deleted -> the configuration is
  gone, Build again… offered.
- ``s4``: RangeSlv L=+10.5 (4L's value set while 2H is active, no other); ModeSlv At 101 with 4WD=+9 (2H's and N's
  values 97); 4H's ModeSlv 4WD -> 2WD (J14: the value and FrontDog's coupling off in 4H); each measured, with a drive;
  then a Modes row 4X -> the structural sentence -> Build again… -> ``_r2`` with five configurations, built and judged
  as s1, every earlier file unchanged.
- ``s5`` (built fresh, the coordinator's ruling 3 of stage 2d): (i) the plan doctored with a second distance mate on
  RangeSlv on in N only (60 mm against N's 56), through the app as it is -> refused at the gate verbatim, nothing made,
  no SolidWorks call; (ii) a coupling the mode step can make, the Sun to LoDog 1 : 1 on in N only (against the
  planetary's 4 : 1, so SolidWorks cannot hold it) -> the build stops in step 5 naming mode N; the parts and layout on
  record, no assembly file, the document open and named; the footer never offering the same build again; closed as
  m4 closes it. The watch tolerates an "Over Defined" balloon from the make to the close.
- ``s7`` (each case on its own copy of s1.master): what a configuration keeps. After every step every configuration is
  shown, rebuilt and read through fresh handles, each body as its turn from its frame on record and its axial
  offset; saved, reopened, read again; each reading judged against "shared by all", "kept per configuration" and the
  coordinator's hypothesis H. Cases: 1 the drive's +37° in 2H on an untouched copy; 2 a no-op put by the app's route
  in 4L, then the drive in 2H; 3 the no-op put in every configuration, then the drive in 2H, in 4L, a reopen, in N; 4
  the app's changed Update, then the drive in 2H; 5 FIdler put in N and 4H by a plain Transform2, FDrive moved along
  its axis by the app's route in 2H; 6 each body put, held or wholly free during the put; 7 a slide's value set in 4L
  with 2H active, a handle held across a show, IsFixed through fresh handles. The readings go to w8-s7-<ts>.json.

The W5 sections, each in its own folder under the output folder (the default order is W8's, W7's, W6's, then m1 m3 m7
m8 m2 m4 m5 m6 a a2 a3 b c; ``--only ring`` runs m3, m7 and m8, the ring-train sections):

- ``m1`` (W5-PLAN §4.3): the Windows-saved 12 : 1 fixture (compound S2). Build turning; §4.1; §4.2 with the
  control on G3 meshes G4. M7: an angle mate the record does not know, on G4, unsuppressed -> Update refuses
  naming it; suppressed -> Update goes through and lists it; deleted. D10: "G4 along S3" suppressed -> Update turns
  it back on and says so. The user's turn, simulated: driven 37° and the drive deleted -> Update with nothing
  changed: nothing put, nothing changed, "… The gears stand where they were turned in SolidWorks."; train_check's
  residuals and each gear's origin, axis and turn residuals logged. Excel G4 At 27 -> 30 ("G4 Face Z" set; see
  AXIAL_RESTORES); G3 At 27 -> 29 (a follower: an Update under suppressed locks), frames, drive; the W4
  demonstration edit (S2 X 63.75 -> 64.5, G2 Teeth 68 -> 69, S3 X following) -> an Update by the remake: G2's
  part, the layout, the gear mate G1 meshes G2 at 17 : 69, every gear put, no lock left off; frames, drive at the
  new ratio, reopen. Then a structural edit (G1 face width 15 -> 17 moves its front face off the Front plane) ->
  Build again… builds Reducer_12to1_r2 turning; every earlier file's sha256 and mtime unchanged; §4.1; §4.2.
- ``m2``: the Arc_Move fixture (S2 placed by formulas from an angle cell). Build; §4.1; §4.2; the user's turn
  (25°) and Update with nothing changed; the angle 30 -> 40 in Excel; SolidWorks' wrong swing logged (the script
  makes the layout move itself, reads where the mates carried each gear, and discards it with QuitDoc); then Update
  moves the layout's shafts and puts the whole train back at its built turn; frames, axes, mates, interference, drive
  at the new place, reopen.

  Every Update with nothing to do (m1, m2, m3 and M7's suppressed press) is judged from SolidWorks too: every gear's
  frame read before and after the press must agree to 1e-6, and every document must read GetSaveFlag False before
  and after it (findings.GEAR_MATE_DEFINITION_READ_MARKS "nothing"). M7's refused press reads the frames, every
  mate's suppression and the marks before and after it: nothing may change.
- ``m3``: the Risky_Placements fixture (Z- shafts, two compound shafts, a helical pinion in a helical ring on Z-,
  herringbones of unequal faces). Build; §4.1 (G3–G4's control under suppressed locks); §4.2 through the whole
  train with the control on the ring's mesh G5 meshes G6; the user's turn (20°) and Update with nothing changed.
- ``m4``: the refused mate, forced (W5-DECISIONS answer 1). The 12 : 1 plan with mates injected by the script
  (G3, the follower locked to G2, also on S2 Axis and along S2 — ``--m4-offset`` mm off where it stands, 0 by
  default). Ruled on 2026-11-14: the consistent mates first; if SolidWorks accepts them, that is logged as a finding
  and the build is forced again, in folder m4-offset1, 1 mm off; the log says which case made the refusal. Then:
  the build stops: AddMate5's statuses, the error codes and warnings, the constrained statuses and the
  app's sentences logged; the parts and the layout part saved and on record, no assembly file, the document left
  open and named, the record's mate problems and their digest; the footer never offers the same build of the
  unchanged workbook. Then a note cell changed in Excel (the plan unchanged, without the injection) -> Build makes
  the assembly at the same revision, beside the refused document left open when the P0c finding says that holds
  (else after closing it); then the refused document closed as W4's ``close_ours`` closes on 2024 (this run's
  modified documents saved first, then ``CloseDoc``).
- ``m5``: an Update lost and pressed again: the 12 : 1 built, the demonstration edit and Update, every document of
  the section closed in SolidWorks without saving (``QuitDoc``), Update pressed again on the same workbook: the
  sentence "… was not saved before … was closed, so its changes were made again", and the drive at 17 : 69 shows
  whether the gear mate holds the ratio the record says.
- ``m6``: mates in a folder (W5-DECISIONS on P0c: a turning Update skips the folder's "FtrFolder" entries). The
  12 : 1 built; its two gear mates put in a mate folder (``findings.MATE_FOLDER_ROUTE``) and found BETWEEN the
  folder's entry and its end tag in the mate group's walk, made, after a save and reopen, and after an Update; Excel
  G3 At 27 -> 29, an Update that puts the whole train: it must pass, every recorded mate found sound in SolidWorks
  (``measure_mates``, the SolidWorks-side check), frames and interference clean. Then S2 X 64.5 and G2 69: the
  remade G1 meshes G2 lands as the mate group's last entry, outside the folder, G3 meshes G4 still inside, through
  a drive at 17 : 69 and a reopen.
- ``m8``: the ring's gear mate made again after a move (2026-11-14: on 2024 a fresh ring gear mate's sense depends
  on where the gears sit when it is made): Risky_Placements built; G5 At 45 -> 47 by Update; then the ring mesh's
  teeth 14/36 -> 15/37 (the centre distance kept) by Update, which remakes G5 meshes G6. Judged from SolidWorks: the
  result's ratios, turned round and sense found wrong logged, the app's read-back of the remade mate (right, its
  axes, its Reverse), and the drive through the ring at 15 : 37 as the judge; the half-pitch controls, every frame,
  the mates, a quiet Update, then a save, reopen and the drive again.
- ``rs1``, ``rs2``, ``rs3`` (not in the default order; run as r1–r3 on 2026-11-14, renamed when W6 took the names):
  a 14-tooth spur pinion shifted +0.3 (rs1) or -0.3 (rs2) inside an
  unshifted 36-tooth spur ring, module 2, the ring's shaft Z- as Risky_Placements', the shafts at the working centre
  distance ``workbook.checks.internal_working_centre`` gives (d3f4dcf): the workbook checks clean, built to turn,
  the app's interference as built, the half-pitch controls, the drive through the mesh with the both-Flips control,
  and interference at a quarter, a half and three quarters of the pinion's pitch. rs3: the +0.3 pair at the plain
  22 mm, which the Checks panel must refuse before any build; its sentence and the fixes offered are logged.
- ``m7``: the ring train edited: Risky_Placements built to turn; G5 At 45 -> 47 (a follower locked to G4, the ring's
  pinion) -> an Update that puts the whole train; frames, mates, interference, the half-pitch controls, the drive
  through the ring with the control on its mesh, reopen.

  Not shown here, and why: M9 (a gear on a shaft held still stays fixed) and M13 (a loop-closing mesh left
  unmated) each need a workbook no committed fixture is — a shaft with Role "fixed" or meshing only a fixed one;
  three shafts meshing in a ring of meshes — so they stay with the fake tests until such a fixture is agreed. An
  Update on a PAIR assembly is not reachable: Update SolidWorks acts only on the workbook's gearbox, and a pair is
  built by the pair window's build_pair with no Update (``swcom.rebuild_call``'s pair kind is gear_pairs_check's).
  M8's failure sentence (a lock that cannot be turned back on) cannot be forced without a call no probe made, so it
  stays with the fake tests.

  No committed fixture has a gear that carries two gear mates (an idler), so the idler tooth change
  (``IDLER_UPDATE_HOLDS``) is not demonstrated through the app here; the 12 : 1 tooth change stays the
  demonstration's.
- ``a``: W4's section a on a turning build: build; §4.1; the demonstration edit as an Update by the remake (W4's
  "G2 at its old frame clashes" control does not hold for mated gears — the axis mate pulls a put gear back — so
  §4.2's drive at 17 : 69 stands in for it); then G1's bore cleared with Update's changes unsaved: the build-again
  plan does not wait for a save (W4 review B2), ``_r2`` built turning, earlier files unchanged.
- ``a2``: a build stopped at the assembly (a template that is not there), carried on; Build pressed again.
- ``a3`` (the second W4 review, N4 and N2): the journal of a build interrupted after two parts; then the
  demonstration edit and Update, closed unsaved; the edit typed back: Update loads every document from its file,
  finds the gear mate already at 17 : 68 (its live ratio, read in the check phase) and remakes nothing, so nothing
  is changed and the record takes 17 : 68; the drive at 17 : 68; package C's sentence pinned.
- ``b``: a workbook written by ``write_new``, S2 placed by formulas: build; §4.1; the angle changed; a part-only
  Update (G2's bore 8 -> 10).
- ``c``: the risky placements written by ``write_new``: build; §4.1.

``--fixtures FOLDER`` copies b's and c's workbooks, as Excel saved them with a neutral Output folder, there; and r1's
and r5's (Bevel_Reducer.xlsx, Crossed_Slant.xlsx) as Excel saved them, their Output folder blank.

Refuses to run unless the session it attaches to is the PID given. Only documents this run made are saved and
closed (its modified parts saved before an assembly is closed: SolidWorks 2024 asks about them in a modal dialog
otherwise); nothing open before the run is touched, and other documents' titles are logged as
``<user document N>``. On SolidWorks 2024 a section starts only with 3 GB of RAM free, and the run stops between
steps if it falls under 2 GB. The log ends with the step only a person can do (W5-PLAN §4.4).
"""

import copy
import ctypes
import dataclasses
import hashlib
import json
import math
import os
import queue
import re
import shutil
import sys
import threading
import time
import traceback

sys.path.insert(0, sys.argv[1])
SRC, OUT = sys.argv[1], sys.argv[2]
PID = int(sys.argv[sys.argv.index("--pid") + 1])
# W6 (W6-PLAN §6.1): the builders r1 and r5 first, then the sections that start from their copies, then the variant.
W6_ORDER = ["r1", "r5", "r2", "r3", "r4", "r6", "r8", "r7"]
# W7 (W7-PLAN §6): p1 builds the master, the rest start from its copies.
W7_ORDER = ["p1", "p2", "p3", "p4", "p5", "p6", "p7"]
# W8 (W8-PLAN §5): s0 the shakedown, s1 the E4 transfer case, kept as s1.master for s2-s4, which copy it.
W8_ORDER = ["s0", "s1", "s2", "s3", "s4", "s5", "s7"]
DEFAULT_ORDER = W8_ORDER + W7_ORDER + W6_ORDER + ["m1", "m3", "m7", "m8", "m2", "m4", "m5", "m6", "a", "a2", "a3", "b", "c"]
RING = ["m3", "m7", "m8"]         # ``--only ring``: the two ring-train sections, rerun after the ring-sense fix
# ``--only confirm``: SolidWorks 2024's confirming build (W6-PLAN §6.1, with W6-INTERFACES §7.17 (a) and (c)): both
# turned fixtures with their both-Flips controls, every turned gear mate made again at a new ratio, and the ring.
CONFIRM = ["r1", "r5", "r3", "r6", "r8", "m3"]
# ``--only confirm7``: SolidWorks 2024's confirming run of W7 (W7-PLAN §6): p1 and p5, where the ring mates are.
ALIASES = {"ring": RING, "w6": W6_ORDER, "confirm": CONFIRM, "planetary": W7_ORDER, "confirm7": ["p1", "p5"],
           "modes": W8_ORDER}
ONLY = [n for i, a in enumerate(sys.argv) if a == "--only"
        for n in ALIASES.get(sys.argv[i + 1], [sys.argv[i + 1]])] or DEFAULT_ORDER
LOG_PATH = sys.argv[sys.argv.index("--log") + 1] if "--log" in sys.argv else os.path.join(OUT, "workbook-assembly.log")
FIXTURES = sys.argv[sys.argv.index("--fixtures") + 1] if "--fixtures" in sys.argv else ""
# ``--p3-steps 1``: p3's steps to run (default all three), for a confirming run of the put-back alone.
P3_STEPS = sys.argv[sys.argv.index("--p3-steps") + 1] if "--p3-steps" in sys.argv else "123"
M4_OFFSET = float(sys.argv[sys.argv.index("--m4-offset") + 1]) if "--m4-offset" in sys.argv else 0.0
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FIXTURE_DIR = os.path.join(REPO, "tests", "fixtures", "excel-windows")
FIXTURE_12 = os.path.join(FIXTURE_DIR, "Reducer_12to1.xlsx")
FIXTURE_ARC = os.path.join(FIXTURE_DIR, "Arc_Move.xlsx")
FIXTURE_RISKY = os.path.join(FIXTURE_DIR, "Risky_Placements.xlsx")

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

os.environ["GG_SRC"] = SRC                     # xlhelp must import the same app as this script
os.environ["GG_EXCEL_SCRATCH"] = os.path.join(OUT, "excel")
sys.path.insert(1, os.path.join(HERE, "excel"))

import win32api  # noqa: E402
import win32gui  # noqa: E402
import win32process  # noqa: E402
import xlhelp  # noqa: E402

from gear_generator import __version__, findings, store, swbuild, swcom, ui_text  # noqa: E402
from gear_generator.gears import base, equations  # noqa: E402
from gear_generator.swcom import call  # noqa: E402
from gear_generator.workbook import assess as wb_assess  # noqa: E402
from gear_generator.workbook import gearbox as wb_gearbox  # noqa: E402
from gear_generator.workbook import geometry as wb_geometry  # noqa: E402
from gear_generator.workbook import layout as wb_layout  # noqa: E402
from gear_generator.workbook import link as wb_link  # noqa: E402
from gear_generator.workbook import model as wb_model  # noqa: E402
from gear_generator.workbook import update as wb_update  # noqa: E402
from gear_generator.workbook import xlsx  # noqa: E402
from gear_generator.workbook.model import Box, Gear, GearboxSpec, Mesh, Shaft  # noqa: E402
from gear_generator.workbook_gui import _had_assembly, _update_gate  # noqa: E402  (the window's own helpers)

LOG = []
FAILS = []
NOTES = []
LOCK = threading.Lock()
STOP = threading.Event()
WRITTEN_BY = f"gear-generator {__version__}"
TAG = {"version": "", "major": 0, "revision": ()}
PERSON = []               # (what, path) of a plain 12 : 1 assembly built to turn, for W5-PLAN §4.4's step
PERSON_W6 = []            # r1's kept Bevel_Reducer.SLDASM, for W6-PLAN §6.1's step
PERSON_W7 = []            # p1's kept Planetary_4to1.SLDASM, for W7-PLAN §6's step

# The driven proof (W5-PLAN §4.2).
DRIVE = "Drive"                      # the assembly global the angle mate's D1 is linked to
DRIVE_MATE = "Demonstration drive"   # the temporary angle mate
CONTROL = "Control "                 # prefix of the temporary gear mate of the wrong-sense control
DRIVE_FROM, DRIVE_TO = 90.0, 120.0
DRIVE_TOLERANCE = 1e-6               # relative, on each gear's turn in degrees (W5-PLAN §4.2)
FRAME_TOLERANCE = 1e-6               # on every origin coordinate (mm) and rotation entry
TURNED_SENTENCE = "The gears stand where they were turned in SolidWorks."
LOST_SENTENCE = "was not saved before Reducer_12to1.SLDASM was closed, so its changes were made again"
# Package C's sentences (9f1e27c), as ui_text gives them for m5 and a3 (pinned from the dry harness, 2026-11-14).
REMADE_SENTENCE = "set the gear mate G1 meshes G2 back to 17 : 69 (SolidWorks held it at 17 : 68), re-placed G1, G2, G3 and G4"
TYPED_BACK_SENTENCE = ("SolidWorks already matches the workbook: nothing was changed. The last Update SolidWorks was not "
                       "saved before Reducer_12to1.SLDASM was closed; SolidWorks already holds the workbook as it now "
                       "is, so nothing needed making again. The gear mate G1 meshes G2 was already 17 : 68 in "
                       "SolidWorks, so it was left as it is.")

# W5-PLAN §4.3 m1 and the user's answer 2: G4 At 27 -> 30 puts the turned train back at its built turn. Ruled on
# 2026-11-14 (an app fault the dry run found, fixed in ba2bc1f): whenever Update moves a gear of a train in any way —
# a put, a Face Z set, a shaft moved under it, a remake — the whole train is put, and ``restored`` names the gears
# that were turned. (So a Face Z change on an UNTURNED train puts every gear too, with ``restored`` empty.)
AXIAL_RESTORES = True

# W8-PLAN §0.5 (review S5): a modal dialog from a configuration call is a STOP. Every SolidWorks member the app (swcom)
# and this script reach goes through ``call``; it is wrapped here so the dialog watcher can say which member was in
# progress when a window came up. A configuration call, or a save or open once this run has made a configuration,
# with a window up is a STOP, unless the window is the same box (title and texts) already seen before any
# configuration was made (the coordinator's ruling: SolidWorks' startup notification, a NOTE).
CALLS = {"now": "", "configurations": False}
CONFIGURATION_CALLS = ("AddConfiguration2", "ShowConfiguration2", "SetSuppression2", "SetSystemValue3",
                       "DeleteConfiguration2")
DOCUMENT_CALLS = ("SaveAs3", "OpenDoc6")
STARTUP_BOXES = set()
# The coordinator's ruling (stage 2a): SolidWorks' notification box — untitled, exactly these six placeholder texts —
# is exempt whenever it comes up, during any call, while nothing answers it and the call returns: a NOTE naming the
# call. Any other window during a configuration call stays a STOP.
NOTIFICATION_TEXTS = ("Title", "Description", "Button1", "Button2", "Hyperlink Text 1", "Hyperlink Text 2")
WINDOWS = {"count": 0}           # windows the watcher logged that were not progress boxes (s3: "no window under the watch")
_RAW_CALL = swcom.call
# A trace of the SolidWorks calls a job makes, kept only while TRACE["on"] (an Update the script judges by its calls:
# W8 s2's put order per mode, s3's "nothing shown, set or put before the refusal"). Each entry: (member, what):
# a configuration's name for a show, the mate's name and the names for a flag call, the value and names for a
# value set, the component's Name2 for a put.
TRACE = {"on": False, "calls": [], "count": 0}     # count: every swcom call while on (s5 (i))
TRACED = ("ShowConfiguration2", "SetSuppression2", "IsSuppressed2", "SetSystemValue3", "DeleteConfiguration2",
          "AddConfiguration2", "ForceRebuild3", "EditRebuild3", "AddMate5", "OpenDoc6", "SaveAs3")


def _names_of(value):
    value = getattr(value, "value", value)
    return list(value) if isinstance(value, (list, tuple)) else value


def _traced_entry(obj, name, args):
    if name in ("IsSuppressed2", "SetSuppression2"):
        try:
            mate = str(_RAW_CALL(obj, "Name"))
        except Exception:  # noqa: BLE001 - the trace must never change what the job does
            mate = "?"
        return (name, mate, args[0] if args else None, _names_of(args[1]) if len(args) > 1 else None) \
            if name == "IsSuppressed2" else (name, mate, args[0] if args else None,
                                              _names_of(args[2]) if len(args) > 2 else None)
    if name == "ShowConfiguration2":
        return (name, args[0] if args else None)
    if name == "SetSystemValue3":
        return (name, args[0] if args else None, _names_of(args[2]) if len(args) > 2 else None)
    return (name,)


def traced_call(obj, name, *args):
    """``swcom.call``, with the member in progress kept in CALLS["now"] for the dialog watcher, and the TRACE kept."""
    if name == "AddConfiguration2":
        CALLS["configurations"] = True
    if TRACE["on"]:
        TRACE["count"] = TRACE.get("count", 0) + 1
        if name in TRACED:
            TRACE["calls"].append(_traced_entry(obj, name, args))
    before, CALLS["now"] = CALLS["now"], name
    try:
        return _RAW_CALL(obj, name, *args)
    finally:
        CALLS["now"] = before


swcom.call = traced_call
call = traced_call
_RAW_PLACE = swcom.Session.place_component


def _traced_place(self, handle, *args, **kwargs):
    """``Session.place_component``, the put kept in the TRACE by the component's Name2 (a put is a ``Transform2``
    put, not a ``call``)."""
    if TRACE["on"]:
        TRACE["calls"].append(("put", self._component_name(handle)))  # noqa: SLF001
    return _RAW_PLACE(self, handle, *args, **kwargs)


swcom.Session.place_component = _traced_place


class Stopped(Exception):
    """Free memory fell under the floor on SolidWorks 2024: the run stops between steps."""


class Halt(Exception):
    """The 90° drive misbehaved (W5-PLAN §4.2: stop and ask): the run stops, nothing more is driven."""


def say(line=""):
    with LOCK:
        print(line, flush=True)
        LOG.append(line)


def check(ok, what):
    say(("ok      " if ok else "FAIL    ") + what)
    if not ok:
        FAILS.append(what)
    return ok


def note(what):
    """Something SolidWorks did beyond what was expected, which is not a failure until the coordinator rules."""
    say("NOTE    " + what)
    NOTES.append(what)


def run(worker, fn, timeout=2400):
    value, error = worker.submit(fn).wait(timeout=timeout)
    if error is not None:
        raise error
    return value


def guard():
    if STOP.is_set():
        raise Stopped("free memory fell under 2 GB on SolidWorks 2024")


# -- the machine ---------------------------------------------------------------------------------------------


class _Memory(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                ("avail", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong), ("b", ctypes.c_ulonglong),
                ("c", ctypes.c_ulonglong), ("d", ctypes.c_ulonglong), ("e", ctypes.c_ulonglong)]


def free_gb():
    m = _Memory()
    m.length = ctypes.sizeof(_Memory)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.avail / 2 ** 30


def sw_private_gb():
    try:
        handle = win32api.OpenProcess(0x1000 | 0x0010, False, PID)   # QUERY_LIMITED_INFORMATION | VM_READ
        try:
            return win32process.GetProcessMemoryInfo(handle)["PagefileUsage"] / 2 ** 30
        finally:
            win32api.CloseHandle(handle)
    except Exception:  # noqa: BLE001
        return float("nan")


def memory():
    return f"SolidWorks {sw_private_gb():.2f} GB private, {free_gb():.2f} GB free"


PROGRESS = {"Calculating Interference Detection": 0, "Updating...": 0, "Opening": 0, "Loading...": 0}
# Set only while this run closes a refused, never-saved assembly by its title (m4): no probe closed one on 2024 under
# a watch, so a "save changes?" box there is answered "Don't Save", as a person closing it unsaved would, and logged.
DISMISS = threading.Event()
DISMISS_BUTTONS = ("&No", "No", "Do&n't Save", "Don't Save", "&Don't Save", "Don't save")
# W6-PLAN §7.1: set only while the first copy's assembly is opened (copy_built step 3). Any dialog then (a
# missing-reference or references-moved prompt) is listed in OPEN_DIALOGS and answered No / Cancel, so the open
# cannot hang the run; one seen drops the copy route, and every later section builds its fixture fresh.
OPENING = threading.Event()
OPEN_DIALOGS = []
OPEN_BUTTONS = DISMISS_BUTTONS + ("Cancel", "&Cancel")


def press_dont_save(hwnd, buttons=DISMISS_BUTTONS):
    """Post BM_CLICK to the dialog's "No"/"Don't Save" button; the button's text, or "" when it has none."""
    found = []

    def each(child, _):
        if win32gui.GetWindowText(child) in buttons:
            found.append(child)
        return True
    try:
        win32gui.EnumChildWindows(hwnd, each, None)
    except Exception:  # noqa: BLE001
        return ""
    if not found:
        return ""
    win32gui.PostMessage(found[0], 0x00F5, 0, 0)      # BM_CLICK
    return win32gui.GetWindowText(found[0])


class DialogWatch(threading.Thread):
    """Logs any dialog SolidWorks shows (it would block every COM call) and, on 2024, sets STOP under 2 GB free.
    It closes nothing: a SolidWorks dialog is for a person to read."""

    def __init__(self):
        super().__init__(daemon=True)
        self.stop = threading.Event()
        self.seen = set()

    def run(self):
        while not self.stop.is_set():
            found, balloons = [], []

            def each(hwnd, _):
                if win32gui.IsWindowVisible(hwnd) and win32process.GetWindowThreadProcessId(hwnd)[1] == PID:
                    kind = win32gui.GetClassName(hwnd)
                    if kind == "#32770":
                        found.append(hwnd)
                    elif kind == "swBalloonTip":
                        balloons.append(hwnd)
                return True
            try:
                win32gui.EnumWindows(each, None)
            except Exception:  # noqa: BLE001
                pass
            for hwnd in balloons:
                # Tier 11 (findings.CONFIGURATION_SHOW_OVER_DEFINED): non-modal, may outlive the call that raised it,
                # came once per run or not at all. None of these sections makes anything over-defined on purpose, so
                # one seen is a NOTE (the mate checks say the rest). Never answered.
                texts = tuple(t for t in [win32gui.GetWindowText(hwnd)] + xlhelp.child_texts(hwnd)[:8] if t)
                if ("balloon", hwnd, texts) not in self.seen:
                    self.seen.add(("balloon", hwnd, texts))
                    now = CALLS["now"]
                    said = (f"a SolidWorks balloon tip {list(texts)} came up while {now or 'no SolidWorks call'} was in "
                            "progress (left standing, never answered)")
                    configuring = now in CONFIGURATION_CALLS or (now in DOCUMENT_CALLS and CALLS["configurations"])
                    if S5_WATCH["on"] and any("Over Defined" in t for t in texts):
                        # s5 makes the assembly over-defined on purpose (W8-REVIEW-TIER11 (3)): tolerated, a fact.
                        S5_WATCH["balloons"].append((now, list(texts)))
                        say(f"fact    {said} (s5's over-defined make: tolerated)")
                    elif any("Over Defined" in t for t in texts) or configuring:
                        note(said)
                    else:                  # the coordinator's ruling 3 (stage 2b): a UI tip, a fact line
                        say(f"fact    {said}")
            for hwnd in found:
                title = win32gui.GetWindowText(hwnd)
                texts = tuple(xlhelp.child_texts(hwnd)[:8])
                if not title and any(t.startswith("Opening Component") for t in texts):
                    title = "Opening"                    # the open-progress box has no title of its own
                # A box is told apart by its handle, title and texts together (review of the run): a handle SolidWorks
                # reuses for a later box is still logged. A progress box, whose texts tick, by its handle alone.
                ticking = title in PROGRESS or any(t.startswith("Elapsed time") for t in texts)
                key = hwnd if ticking else (hwnd, title, texts)
                if key not in self.seen:
                    self.seen.add(key)
                    if title in PROGRESS:              # SolidWorks' own progress box: said once, then counted
                        PROGRESS[title] += 1
                        if PROGRESS[title] > 1:
                            continue
                    say(f"DIALOG  SolidWorks shows {title!r}: {xlhelp.child_texts(hwnd)[:8]}"
                        + (" (a progress box that closes itself; not logged again)" if title in PROGRESS else ""))
                    if "SOLIDWORKS CAM" in title and any(t.startswith("Save changes to") for t in texts):
                        # Closing a changed 2024-era assembly in 2026 raises this Yes/No box, which ignores WM_CLOSE
                        # and Escape (it held a probe 50 minutes). Every close of this run saves first or means to
                        # discard, so No is what a person would press.
                        pressed = press_dont_save(hwnd)
                        say(f"DIALOG  SOLIDWORKS CAM's save question answered: pressed {pressed!r}")
                    elif DISMISS.is_set() and title not in PROGRESS:
                        pressed = press_dont_save(hwnd)
                        say(f"DIALOG  closing a refused, never-saved assembly: pressed {pressed!r}" if pressed else
                            "DIALOG  closing a refused, never-saved assembly: no No / Don't Save button to press")
                    elif OPENING.is_set() and not ticking:
                        OPEN_DIALOGS.append((title, texts))
                        pressed = press_dont_save(hwnd, OPEN_BUTTONS)
                        say(f"DIALOG  opening a copied assembly (W6-PLAN §7.1): pressed {pressed!r}; the copy route "
                            "is dropped")
                    elif not title and tuple(texts) == NOTIFICATION_TEXTS:
                        WINDOWS["count"] += 1
                        note(f"SolidWorks' notification box came up while {CALLS['now'] or 'no SolidWorks call'} was in "
                             "progress (exempt by the coordinator's ruling; nothing answers it)")
                    elif not ticking and S5_WATCH["on"]:
                        # s5, from the make to the close: any window but the balloon and the exempt boxes is a STOP.
                        WINDOWS["count"] += 1
                        S5_WATCH["windows"].append((CALLS["now"], title, list(texts)))
                        check(False, f"s5: a SolidWorks window {title!r} {list(texts)} came up while "
                                     f"{CALLS['now'] or 'no SolidWorks call'} was in progress, between the make and the "
                                     "close")
                        STOPS.append(f"s5: a window {title!r} came up while {CALLS['now']} was in progress")
                        say("STOP    W8-REVIEW-TIER11 (3): s5's watch allows only the Over Defined balloon")
                    elif not ticking:
                        WINDOWS["count"] += 1
                        now = CALLS["now"]
                        box = (title, texts)
                        if not CALLS["configurations"]:
                            STARTUP_BOXES.add(box)
                        configuring = now in CONFIGURATION_CALLS or (now in DOCUMENT_CALLS and CALLS["configurations"])
                        if configuring and box not in STARTUP_BOXES:
                            check(False, f"a SolidWorks window {title!r} {list(texts)} came up while {now} was in "
                                         "progress, after this run made a configuration")
                            STOPS.append(f"a window {title!r} came up while {now} was in progress")
                            say("STOP    W8-PLAN §0.5: a modal dialog during a configuration call")
                        else:
                            note(f"a SolidWorks window {title!r} {list(texts)} came up while "
                                 f"{now or 'no SolidWorks call'} was in progress"
                                 + (" (the same box was seen before any configuration was made)" if configuring else
                                    "" if CALLS["configurations"] else ", before this run made any configuration"))
            if TAG["major"] == 32 and free_gb() < 2.0 and not STOP.is_set():
                say(f"STOP    {memory()}: under 2 GB free, the run stops at the next step")
                STOP.set()
            time.sleep(2)


# -- documents -----------------------------------------------------------------------------------------------


def documents(app):
    out, doc = [], call(app, "GetFirstDocument")
    while doc is not None:
        out.append(doc)
        doc = call(doc, "GetNext")
    return out


def ours(path):
    """Whether a document is under this run's output folder: matched with a separator, so a folder whose name
    merely starts with OUT's (asm2026b beside asm2026) is not taken for it."""
    root = os.path.normcase(os.path.abspath(OUT)).rstrip("\\/") + os.sep
    return bool(path) and os.path.normcase(os.path.abspath(path)).startswith(root)


USERS = {}
REFUSED = []              # titles of refused, never-saved assemblies this run left open (m4), closed by title


def open_titles(session):
    """Every open document's title; one not made by this run as ``<user document N>`` (the repo is public)."""
    out = []
    for doc in documents(session._app):  # noqa: SLF001
        title, path = str(call(doc, "GetTitle")), str(call(doc, "GetPathName") or "")
        if ours(path) or (not path and title in REFUSED):
            out.append(title)
        else:
            USERS.setdefault(path or title, f"<user document {len(USERS) + 1}>")
            out.append(USERS[path or title])
    return out


def save_docs(session, paths):
    """Save the open documents at these paths, as a person would in SolidWorks; returns what was saved."""
    saved = []
    for doc in documents(session._app):  # noqa: SLF001
        path = str(call(doc, "GetPathName") or "")
        if any(store.same_path(path, p) for p in paths):
            ok = call(call(doc, "Extension"), "SaveAs3", path, 0, 1, swcom._null_dispatch(),  # noqa: SLF001
                      swcom._null_dispatch(), swcom._out_long(), swcom._out_long())  # noqa: SLF001
            saved.append((os.path.basename(path), bool(ok)))
    return saved


def close_ours(session):
    """Save this run's modified documents, then close them, assemblies first; then any refused assembly this run
    left open, by its title (it has no file). Returns what is left open of ours."""
    app = session._app  # noqa: SLF001
    saved = []
    for doc in documents(app):
        path = str(call(doc, "GetPathName") or "")
        if ours(path) and call(doc, "GetSaveFlag"):
            call(call(doc, "Extension"), "SaveAs3", path, 0, 1, swcom._null_dispatch(),  # noqa: SLF001
                 swcom._null_dispatch(), swcom._out_long(), swcom._out_long())  # noqa: SLF001
            saved.append(os.path.basename(path))
    if saved:
        say(f"        closing: saved this run's modified documents first, as a person would: {saved}")
    for doc in documents(app):
        title = str(call(doc, "GetTitle"))
        if not str(call(doc, "GetPathName") or "") and title in REFUSED:
            DISMISS.set()
            try:
                call(app, "CloseDoc", title)
            finally:
                DISMISS.clear()
            say(f"        closing: the refused assembly {title}, never saved, closed by its title")
    for kind in (2, 1):
        for doc in documents(app):
            if ours(str(call(doc, "GetPathName") or "")) and int(call(doc, "GetType")) == kind:
                call(app, "CloseDoc", str(call(doc, "GetTitle")))
    return [str(call(d, "GetTitle")) for d in documents(app)
            if ours(str(call(d, "GetPathName") or "")) or (not str(call(d, "GetPathName") or "")
                                                            and str(call(d, "GetTitle")) in REFUSED)]


def quit_in(folder):
    """Close the open documents under ``folder`` WITHOUT saving them (``ISldWorks::QuitDoc``), assemblies first, as
    a person closing SolidWorks and answering "Don't save" would. Returns what is left open under it."""
    def under(path):
        return bool(path) and os.path.normcase(os.path.abspath(path)).startswith(
            os.path.normcase(os.path.abspath(folder)) + os.sep)

    def work(session):
        app = session._app  # noqa: SLF001
        for kind in (2, 1):
            for doc in documents(app):
                if under(str(call(doc, "GetPathName") or "")) and int(call(doc, "GetType")) == kind:
                    call(app, "QuitDoc", str(call(doc, "GetTitle")))
        return [str(call(d, "GetTitle")) for d in documents(app) if under(str(call(d, "GetPathName") or ""))]
    return work


def save_flags(session, paths):
    out = {}
    for doc in documents(session._app):  # noqa: SLF001
        path = str(call(doc, "GetPathName") or "")
        for wanted_path in paths:
            if store.same_path(path, wanted_path):
                out[os.path.basename(wanted_path)] = bool(call(doc, "GetSaveFlag"))
    return out


def marked(flags):
    """The documents SolidWorks reads ``GetSaveFlag`` True in (one not open reads nothing, so it is not marked)."""
    return sorted(n for n, f in flags.items() if f)


def expected_marks(result, assembly):
    """What SolidWorks should mark modified after an Update: every document whose content it changed
    (``GearboxUpdate.changed``), and the assembly whenever Update rebuilt it, which also runs the interference
    check — each of which marks the assembly (probe assembly_rebuild_scope) though it holds nothing new."""
    names = {os.path.basename(p) for p in result.changed}
    if result.rebuilt:
        names.add(os.path.basename(assembly))
    return sorted(names)


def check_marks(flags, wanted_marks, label):
    """SolidWorks' marks against what the invariant expects: equal is ok; a superset is a NOTE (logged for the
    coordinator to rule, not a failure: "LOG rather than assume wherever SolidWorks marks more"); one expected
    and missing is a FAIL."""
    got = marked(flags)
    if got == sorted(wanted_marks):
        return check(True, f"{label}: SolidWorks marks modified exactly {got}")
    if set(wanted_marks) <= set(got):
        note(f"{label}: SolidWorks marks modified more than the invariant expects: marked {got}, expected "
             f"{sorted(wanted_marks)} (more: {sorted(set(got) - set(wanted_marks))})")
        return True
    return check(False, f"{label}: SolidWorks marks modified {got}, expected {sorted(wanted_marks)} (missing "
                        f"{sorted(set(wanted_marks) - set(got))})")


def check_fresh_build_marks(worker, paths, assembly, label):
    """Right after a build and its saves: no part and no layout part reads GetSaveFlag True (the assembly is rebuilt
    top-only: findings.ASSEMBLY_REBUILD_ROUTE for W4's static one, MATED_BUILD_REBUILD_ROUTE for a train, which
    probe round P0b saw mark nothing but the assembly), and the assembly does (a read after its save marks it)."""
    flags = run(worker, lambda s: save_flags(s, paths))
    say(f"        marked modified in SolidWorks right after the build: {flags}")
    check(flags.get(os.path.basename(assembly)) is True, f"{label}: the assembly is marked after the build (a read "
          "after its save)")
    check_marks(flags, [os.path.basename(assembly)], f"{label}, right after the build and its saves")


def save_assembly(worker, desk, why):
    """Save the current assembly (and every document of the gearbox SolidWorks holds modified), as a person would,
    so the marks after the next step are that step's own."""
    box = desk.record.gearbox
    paths = [box.assembly, box.layout] + sorted({c.part for c in box.components}) + [c.path for c in carriers_of(box)]
    saved = run(worker, lambda s: save_docs(s, paths))
    say(f"person  saved in SolidWorks ({why}): {saved}")


def sidecar_texts(folder):
    """Every .gear.json in a folder, parsed, by name: taken before a build so a rewritten one can be said field by
    field."""
    import json
    out = {}
    for name in sorted(os.listdir(folder)):
        if name.endswith(".gear.json"):
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                out[name] = json.load(handle)
    return out


def _flat(value, prefix=""):
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            out.update(_flat(item, f"{prefix}.{key}" if prefix else str(key)))
        return out
    return {prefix: value}


def check_earlier_unchanged(folder, earlier, label, earlier_sidecars=None):
    """A build beside earlier files: every earlier SolidWorks file's sha256 and mtime unchanged. A .gear.json may be
    rewritten only to take off the unsaved mark an Update left on it (``finish_build`` unmarks a reused part whose
    changes were saved since; ruled on 2026-11-14); each one that changed is logged with what changed in it, and any
    other change to an earlier file is a FAIL."""
    later = stamps(folder)
    now = sidecar_texts(folder)
    for name in sorted(earlier_sidecars or {}):
        if name in now and now[name] != earlier_sidecars[name]:
            a, b = _flat(earlier_sidecars[name]), _flat(now[name])
            diff = {k: (a.get(k), b.get(k)) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)}
            say(f"fact    {label}: {name} rewritten: {diff}")
    touched = [n for n in earlier if later.get(n) != earlier[n]]
    solid = [n for n in touched if n.upper().endswith((".SLDPRT", ".SLDASM"))]
    check(solid == [], f"{label}: every earlier SolidWorks file's sha256 and mtime unchanged: changed {solid}")
    for name in (n for n in touched if n not in solid):
        part = os.path.join(folder, name[:-len(".gear.json")] + ".SLDPRT") if name.endswith(".gear.json") else ""
        sidecar = store.read_sidecar(part) if part else None
        check(sidecar is not None and sidecar.record.unsaved_since == 0,
              f"{label}: {name} rewritten only to take off Update's unsaved mark (unsaved_since "
              f"{sidecar and sidecar.record.unsaved_since})")
    return later


def stamps(folder, solidworks_only=False):
    """sha256 and mtime of every file in a folder but the link record and Excel's lock file (only the SolidWorks
    documents with ``solidworks_only``: the workbook is Excel's and the sidecars the app's to rewrite)."""
    out = {}
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if not os.path.isfile(path) or name.startswith("~$") or name.endswith(store.LINK_SUFFIX):
            continue
        if solidworks_only and not name.upper().endswith((".SLDPRT", ".SLDASM")):
            continue
        with open(path, "rb") as handle:
            out[name] = (hashlib.sha256(handle.read()).hexdigest(), os.stat(path).st_mtime_ns)
    return out


# -- geometry ------------------------------------------------------------------------------------------------


def turn_about_z(rotation, degrees):
    """A frame's rotation turned about the part's own axis (its local Z): R · rot_z(degrees)."""
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    r = [rotation[i * 3:(i + 1) * 3] for i in range(3)]
    z = ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))
    return tuple(sum(r[i][k] * z[k][j] for k in range(3)) for i in range(3) for j in range(3))


def frame_error(live, wanted_frame, pitch):
    """(largest origin difference in mm, the turn between them in degrees modulo pitch, off-axis residue)."""
    (ra, at_a), (rb, at_b) = live, wanted_frame
    origin = max(abs(float(a) - float(b)) for a, b in zip(at_a, at_b))
    a = [[float(ra[i * 3 + j]) for j in range(3)] for i in range(3)]
    b = [[float(rb[i * 3 + j]) for j in range(3)] for i in range(3)]
    m = [[sum(a[k][i] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    turn = math.degrees(math.atan2(m[1][0], m[0][0]))
    off = turn % pitch if pitch else turn
    off = min(off, pitch - off) if pitch else abs(off)
    residue = max(abs(m[2][2] - 1.0), abs(m[0][2]), abs(m[1][2]), abs(m[2][0]), abs(m[2][1]))
    return origin, off, residue


def frame_gap(a, b):
    """The largest difference between two frames, origin coordinates (mm) and rotation entries alike."""
    (ra, at_a), (rb, at_b) = a, b
    return max([abs(float(x) - float(y)) for x, y in zip(at_a, at_b)]
               + [abs(float(x) - float(y)) for x, y in zip(ra, rb)])


def frames_gap(found, wanted_frames):
    """(the largest frame_gap over the gears, the gear it is at)."""
    worst = (0.0, "")
    for gear, frame in wanted_frames.items():
        gap = frame_gap(found[gear], frame) if gear in found else float("inf")
        if gap > worst[0]:
            worst = (gap, gear)
    return worst


def turn_degrees(rotation_a, rotation_b):
    """``swbuild.turn_between`` in degrees, or None when b is not a's turned about its own Z."""
    turn = swbuild.turn_between(rotation_a, rotation_b)
    return None if turn is None else math.degrees(turn)


# -- the app's Tk-thread side, as the Workbook window has it -------------------------------------------------


class Desk:
    """The Workbook window without Tk: the same calls, in the same order, on this thread."""

    def __init__(self, path, worker, strip=""):
        self.path = path
        self.link = wb_link.Link(path)
        self.worker = worker
        self.strip = strip         # the strip's Output folder (W6: the fixtures leave the Box's blank, W6-PLAN §5)
        self.reading = None
        self.a = None
        self.record = None
        self.record_problem = ""
        self.plan = None
        self.update = None
        self.note = None
        self.error = None          # the last job's raise (a refusal before anything was made or changed)
        self.positions_per_configuration = None   # the last job's answer, as the window keeps it (W8 §9.12)
        self.steps = []            # the last build's progress steps

    # reading
    def read(self):
        deadline = time.monotonic() + 10
        while True:
            try:
                self.reading = self.link.read()
                break
            except xlsx.NotReady as exc:
                if time.monotonic() > deadline:
                    raise
                say(f"        not ready yet: {exc}")
                time.sleep(0.5)
        self._after_read()

    def poll(self, timeout=30.0):
        started = time.monotonic()
        while time.monotonic() - started < timeout:
            reading = self.link.poll()
            if reading is not None:
                if self.reading is None or reading.digest != self.reading.digest:
                    self.note = None       # as the window: the file has moved on from the last job's sentence
                self.reading = reading
                say(f"poll    a new read {time.monotonic() - started:.1f} s after asking; changes:")
                for line in reading.changes:
                    say(f"          {line}")
                self._after_read()
                return reading
            time.sleep(0.25)
        raise AssertionError(f"Link.poll saw no change in {timeout:g} s")

    def _after_read(self):
        r = self.reading
        check(r.ok, f"read {os.path.basename(self.path)}: {r.error or 'ok'}")
        spec = r.spec
        self.a = wb_assess.assess(spec, r.diagnostics, self.folder(spec), spec.box.part_template)
        for d in self.a.diagnostics:
            say(f"        {d.level:7} {d.message}")
        say(f"        {len(spec.shafts)} shafts · {len(spec.gears)} gears · {len(spec.meshes)} meshes; "
            f"gate {self.a.lay_out_refusal()!r}")
        self.plan_solidworks()

    def folder(self, spec):
        """``WorkbookWindow._folder``: the Box sheet's Output folder, else the strip's."""
        return spec.box.output_folder or self.strip

    def plan_solidworks(self):
        """``WorkbookWindow._plan_solidworks_pass`` (the record is always this workbook's here)."""
        newer = False
        try:
            record, problem = store.read_link_record(self.path), ""
        except store.UnknownSchema as exc:
            record, problem, newer = None, str(exc), True
        except store.StoreError as exc:
            record, problem = None, str(exc)
        if record is not None:
            store.clear_saved(record)
        self.record, self.record_problem = record, problem
        self.plan = self.update = None
        a = self.a
        if a is None or newer:
            return
        gearbox = record.gearbox if record is not None else None
        has_assembly = gearbox is not None and bool(gearbox.assembly)
        parts_only = not has_assembly and bool(a.parts.refused)
        gate = a.build_refusal() if parts_only else a.lay_out_refusal()
        if not gate:
            self.plan = wb_gearbox.plan_gearbox(a, record, parts_only=parts_only)
        if record is not None and (record.parts or gearbox is not None) and not _update_gate(a, record):
            self.update = wb_update.classify(record, a)

    def footer(self):
        folder = self.folder(self.reading.spec) if self.reading is not None else ""
        return ui_text.workbook_footer(self.a, record=self.record, record_problem=self.record_problem,
                                       plan=self.plan, update=self.update, folder=folder,
                                       folder_exists=bool(folder) and os.path.isdir(folder), note=self.note,
                                       digest=self.reading.digest if self.reading is not None else "",
                                       positions_per_configuration=self.positions_per_configuration)

    def say_footer(self, when):
        f = self.footer()
        say(f"footer  ({when}) [{'green' if f.ok else 'red'}] {f.text}")
        say(f"        button {f.build_label!r} {'on' if f.build_enabled else 'off'}"
            f"{' primary' if f.build_primary else ''}; Update SolidWorks "
            f"{('shown ' + ('on' if f.update_enabled else 'off') + (' primary' if f.update_primary else '')) if f.update_shown else 'hidden'}")
        return f

    def say_plan(self, full=True):
        p = self.plan
        if p is None:
            say("plan    none (the gate refuses)")
            return
        say(f"plan    revision {p.revision} {p.name}: refusal {p.refusal!r}; reason {p.revision_reason!r}; "
            f"turning {p.motion is not None}; static reason {p.static_reason!r}")
        if p.refusal:
            return
        say(f"        layout {p.layout_path}; assembly {p.assembly_path}")
        for job in p.build:
            say(f"        build {job.stem} for {', '.join(job.gear_ids)} at {job.path} ({len(job.plan.ops)} ops)")
        for r in p.reuse:
            say(f"        reuse {r.stem} for {', '.join(r.gear_ids)} at {r.path} (made by revision {r.revision}, "
                f"{len(r.variables)} globals checked live)")
        if isinstance(p.layout, wb_gearbox.LayoutReuse):
            say(f"        reuse layout {p.layout.path}: {[f'{v.name} = {v.expression}' for v in p.layout.variables]}; "
                f"features {list(p.layout.features)}")
        for s in p.shafts:
            say(f"        shaft {s.shaft}: ({s.x:g}, {s.y:g}, {s.z:g}) axis {s.axis} {tuple(s.direction)} sigma "
                f"{s.sigma:+d}; X {s.x_side} {s.x_global!r}, Y {s.y_side} {s.y_global!r}, Z {s.z_side} "
                f"{s.z_global!r}; line {s.line!r}; {s.axis_name}")
        for gear, f in p.frames.items():
            say(f"        frame {gear}: R {[round(v, 9) for v in f.rotation]} at {[round(v, 9) for v in f.at]}")
        if p.motion is not None:
            m = p.motion
            say(f"        motion: trains {list(m.trains)}; drag {list(m.drag)}; fixed {list(m.fixed)}; unmated "
                f"{list(m.unmated)}")
            for mate in m.mates:
                say(f"        mate {mate.name!r}: {mate.kind} {list(mate.gears)} {mate.shaft} ratio {list(mate.ratio)} "
                    f"face {mate.face_global!r} z_front {mate.z_front:g} plane {getattr(mate, 'plane', '')!r} sense "
                    f"{getattr(mate, 'sense', '')}")
        if full:
            for plan in (p.layout, p.assembly):
                if isinstance(plan, base.BuildPlan):
                    say(f"        ops of {os.path.basename(plan.path)}:")
                    for op in plan.ops:
                        say(f"          {base.describe(op)}")

    def say_update(self):
        u = self.update
        if u is None:
            say("update  none")
            return
        say(f"classify parts changed {[os.path.basename(p.path) for p in u.changed_parts]}; moved "
            f"{list(u.moved_shafts)}; re-place {list(u.replaced)}; structural {list(u.structural)}; missing "
            f"{list(u.missing)}; unsaved {[os.path.basename(p) for p in u.unsaved]}; refusal {u.refusal!r}; "
            f"turning {u.motion is not None}; axial {list(getattr(u, 'axial', ()))}; ratios "
            f"{list(getattr(u, 'ratios', ()))}")
        if u.layout is not None:
            say(f"        layout globals wanted {[f'{v.name} = {v.expression}' for v in u.layout.variables]}")
        say(f"summary {ui_text.update_summary(u)}")

    # the jobs
    def write_journal(self, plan):
        """``WorkbookWindow._write_journal``: what the build is about to make, merged into the record's journal."""
        try:
            record = store.read_link_record(self.path)
        except Exception:  # noqa: BLE001 - as the window: left for the finish
            return False
        if record is None:
            record = store.LinkRecord(workbook=self.path)
        record.pending = wb_gearbox.merged_journal(record, wb_gearbox.journal(plan), self.path)
        record.pending_for = self.path
        try:
            store.save_link_record(record, store.link_record_path(self.path))
        except Exception:  # noqa: BLE001
            return False
        return True

    def build(self, plan=None):
        """``_start_build`` (its journal first) then, once the worker answers, ``_finish_build`` — or, for a raise,
        ``_collect_job``'s ``job_failed`` sentence. ``plan`` (m4 only): a plan the script changed, run in place of
        the window's own."""
        plan = plan or self.plan
        before = self.record                    # the record the build is planned from: Build again… if it held one
        steps = self.steps = []
        kwargs = plan.build_kwargs()
        journaled = self.write_journal(plan)
        say(f"journal {'written' if journaled else 'NOT written'}: {len(wb_gearbox.journal(plan))} paths")
        started = time.monotonic()
        say(f"build   {plan.name}: {memory()}")
        result, self.error = self.worker.submit(
            lambda s: swbuild.build_gearbox(s, **kwargs, progress=steps.append)).wait(timeout=2400)
        seconds = time.monotonic() - started
        if self.error is not None:
            say(f"        raised {type(self.error).__name__}: {self.error}")
            self.note = (ui_text.job_failed(self.error, False), False)
            say(f"status  [red] {self.note[0]}")
            self.plan_solidworks()
            return plan, None
        self.positions_per_configuration = getattr(result, "positions_per_configuration", None)
        for line in result.log_lines():
            say("        " + line)
        say(f"        in {seconds:.1f} s; {memory()}; kind {result.kind!r}; turned round (made again with the other "
            f"Flip) {getattr(result.assembly, 'turned_round', None) if result.assembly is not None else None}")
        say(f"        steps {[(x.stage, x.name, x.index, x.count) for x in steps]}")
        say(f"        progress words {[ui_text.progress_text(x) for x in steps[:1] + steps[-1:]]}")
        self.note = self.finish_build(plan, result, again=_had_assembly(before))
        say(f"status  [{'green' if self.note[1] else 'red'}] {self.note[0]}")
        self.plan_solidworks()
        return plan, result

    def finish_build(self, plan, result, again=False):
        text, ok = ui_text.gearbox_status(plan, result, again=again)
        record, may_write, notes = self._open_record()
        finished = wb_gearbox.finish_build(plan, result, record, workbook=self.path, digest=self.reading.digest,
                                           written_by=WRITTEN_BY)
        if record is None and finished.record is not None:
            finished.record.own_digest = self.link.own_digest
        faults = self._write(finished, may_write)
        if not may_write:
            faults, notes = notes + faults, []
        return " ".join([text] + notes + faults), ok and not faults

    def update_solidworks(self):
        """``press_update`` (no new revision needed) then ``_finish_update``; a raise is ``_collect_job``'s
        ``job_failed`` sentence (``self.error``; the result and the finish are then None)."""
        update = self.update
        steps = []
        kwargs = update.update_kwargs()
        started = time.monotonic()
        say(f"update  {memory()}")
        result, self.error = self.worker.submit(
            lambda s: swbuild.update_gearbox(s, **kwargs, progress=steps.append)).wait(timeout=2400)
        seconds = time.monotonic() - started
        if self.error is not None:
            say(f"        raised {type(self.error).__name__} in {seconds:.1f} s: {self.error}")
            self.note = (ui_text.job_failed(self.error, True), False)
            say(f"status  [red] {self.note[0]}")
            self.plan_solidworks()
            return update, None, None
        self.positions_per_configuration = getattr(result, "positions_per_configuration", None)
        for line in result.log_lines():
            say("        " + line)
        say(f"        in {seconds:.1f} s; {memory()}")
        say(f"        steps {[(x.stage, x.name, x.index, x.count) for x in steps]}")
        say(f"        loaded from disk {[os.path.basename(p) for p in result.opened]}")
        say(f"        motion: turned {result.turned}; out of step {result.out_of_step}; off axis {result.off_axis}; "
            f"restored {result.restored}; unsuppressed {result.unsuppressed}; axial {result.axial}; ratios "
            f"{result.ratios}; extra mates {result.extra_mates}; ratios found {result.ratios_found}, already "
            f"{result.ratios_already}, read {result.ratios_read}; sense found wrong "
            f"{getattr(result, 'sense_found_wrong', None)}, turned round {getattr(result, 'turned_round', None)}")
        say(f"        train_check residuals (rad) {[(a, b, f'{r:.2e}') for a, b, r in result.residuals]}")
        record, may_write, notes = self._open_record()
        base_record = record if record is not None else self.record
        finished = wb_update.finish_update(update, result, base_record, digest=self.reading.digest,
                                           workbook=self.path)
        gearbox = self.record.gearbox if self.record is not None else None
        say(f"        finish: dragged {finished.dragged}; earlier update {getattr(finished, 'earlier_update', '')!r}")
        wrong = list(getattr(result, "sense_found_wrong", []) or [])
        check(not wrong, f"the Update's check phase found no gear mate turning against its mesh: {wrong}")
        if self.record is not None and self.record.gearbox is not None and self.record.gearbox.assembly:
            held = TURNED.setdefault(os.path.normcase(self.record.gearbox.assembly), set())
            held.difference_update(list(result.ratios) + wrong)
            held.update(getattr(result, "turned_round", []) or [])
        text, ok = ui_text.gearbox_update_status(update, result, finished.dragged,
                                                 meshes=gearbox.meshes if gearbox is not None else None,
                                                 finished=finished)
        faults = self._write(finished, may_write)
        if not may_write:
            faults, notes = notes + faults, []
        self.note = (" ".join([text] + notes + faults), ok and not faults)
        say(f"status  [{'green' if self.note[1] else 'red'}] {self.note[0]}")
        self.plan_solidworks()
        if self.record is not None and self.record.gearbox is not None and self.record.gearbox.assembly:
            note_made(self, list(result.ratios) + list(getattr(result, "turned_round", []) or [])
                      + list(getattr(result, "sense_found_wrong", []) or []))
        return update, result, finished

    def _open_record(self):
        try:
            return store.open_link_record(self.path), True, []
        except store.UnknownSchema as exc:
            return None, False, [str(exc)]
        except store.StoreError as exc:
            return None, True, [str(exc)]

    def _write(self, finished, may_write):
        faults = []
        for path, sidecar in finished.sidecars:
            try:
                store.save(path, sidecar)
            except OSError as exc:
                faults.append(ui_text.sidecar_unwritten(path, exc))
        if finished.record is not None and may_write:
            try:
                store.save_link_record(finished.record, store.link_record_path(self.path))
            except store.StoreError as exc:
                faults.append(str(exc))
        say(f"record  {len(finished.sidecars)} sidecar(s) written; record "
            f"{'written' if finished.record is not None and may_write else 'not written'}; notes {finished.notes}")
        return faults + list(finished.notes)

    def plan_shafts(self):
        return wb_layout.shaft_layouts(self.a.spec)


def turning(desk):
    box = desk.record.gearbox if desk.record is not None else None
    return box is not None and bool(box.assembly) and box.kind == store.GEARBOX_MOTION


def edit(desk, book, *cells):
    """Excel sets the cells and saves; the window's poll reads it, plans and classifies."""
    for sheet, ref, value in cells:
        book.set(sheet, ref, value)
    book.save()
    desk.poll()
    desk.say_update()


# -- measuring ----------------------------------------------------------------------------------------------


def in_assembly(asm, work):
    """A worker job: the assembly opened as the app opens it (``open_document``), ``work(session)``, the build
    ended whatever happened."""
    def job(session):
        session.begin_build()
        try:
            session.open_document(asm)
            return work(session)
        finally:
            session.end_build()
    return job


def live_frames(session, asm, names):
    def work(s):
        out = {}
        for index, name in enumerate(names):
            s.find_component(f"m{index}", name)
            out[name] = s.component_frame(f"m{index}")
        return out
    return in_assembly(asm, work)(session)


def live_axes(session, path, names):
    """Each layout axis's ``GetRefAxisParams`` (two points on it, metres), and the layout's globals."""
    def work(s):
        out = {}
        for name in names:
            feature = s._by_name(name)  # noqa: SLF001
            out[name] = [float(v) for v in call(call(feature, "GetSpecificFeature2"), "GetRefAxisParams")]
        return out, s.equation_values()
    return in_assembly(path, work)(session)


def live_globals(session, path):
    return in_assembly(path, lambda s: s.equation_values())(session)


def live_interferences(session, asm):
    return in_assembly(asm, lambda s: s.interferences())(session)


def live_mates(session, asm, components):
    """Every mate as ``mate_states`` reads it, the names of anything else in the mate group, and each gear's
    ``GetConstrainedStatus`` (``components``: (gear, Name2) pairs)."""
    def work(s):
        others = []
        states = s.mate_states(others=others)
        status = {}
        for index, (gear, name) in enumerate(components):
            s.find_component(f"k{index}", name)
            status[gear] = s.constrained_status(f"k{index}")
        return states, others, status
    return in_assembly(asm, work)(session)


def delete_mate(session, name):
    """``findings.MATE_DELETE_ROUTE`` ("Select2 then EditDelete()"), as swcom's remake deletes a gear mate: the mate
    selected alone, ``EditDelete()`` invoked, and its name read gone from the mate group."""
    feature = session._mate_feature(name)  # noqa: SLF001
    doc = session._doc()  # noqa: SLF001
    call(doc, "ClearSelection2", True)
    call(feature, "Select2", False, 0)
    swcom._guarded("EditDelete", lambda: doc.EditDelete())  # noqa: SLF001
    call(doc, "ClearSelection2", True)
    if name in session._mate_names():  # noqa: SLF001
        raise swcom.SolidWorksError(f"The mate {name} is still there after EditDelete().")


def placed_elsewhere(session, asm, name, rotation, at, kind, locks=()):
    """Put one component at another frame, read the interferences, put it back, read them again; with ``locks``
    (mate names), each suppressed around the puts and turned back on after, whatever happened."""
    def work(s):
        for index, lock in enumerate(locks):
            s.find_mate(f"lock{index}", lock)
            s.set_mate_suppressed(f"lock{index}", True)
        try:
            if locks:
                s.rebuild(kind=kind)
            s.find_component("moved", name)
            before = s.component_frame("moved")
            s.place_component("moved", rotation, at, kind=kind)
            moved = s.interferences()
            s.place_component("moved", before[0], before[1], kind=kind)
            back = s.interferences()
            return moved, back
        finally:
            for index, _ in enumerate(locks):
                s.set_mate_suppressed(f"lock{index}", False)
            if locks:
                s.rebuild(kind=kind)
    return in_assembly(asm, work)(session)


def wanted(desk):
    """Each gear's wanted frame and pitch, from the current read (what the window would place); W7: each carrier's
    too, by its carrier id (``layout.carrier_frame``, pitch 0)."""
    frames = wb_layout.frames(desk.a.report)
    placed = desk.a.report.layout.placed
    out = {g: (f.rotation, f.at, wb_layout.pitch(placed[g])) for g, f in frames.items()}
    for carrier in carrier_layouts(desk):
        f = wb_layout.carrier_frame(carrier)
        out[wb_layout.carrier_id(carrier.shaft)] = (f.rotation, f.at, 0.0)
    return out


def carrier_layouts(desk):
    """The read's carriers (W7), or () for a gearbox with none."""
    if desk.a is None or not getattr(desk.a.report, "stages", ()):
        return ()
    return tuple(wb_layout.carrier_layouts(desk.a.spec, desk.a.report))


def carriers_of(box):
    """The record's carriers (W7; schema 5), or [] for a record with none."""
    return list(getattr(box, "carriers", []) or [])


def bodies(box):
    """Every turning or held body of the record: (body id, Name2), gears and copies first, then each carrier by its
    carrier id."""
    return ([(c.gear, c.name) for c in box.components]
            + [(wb_layout.carrier_id(c.shaft), c.component) for c in carriers_of(box)])


def measure_frames(worker, desk, label, exact=None):
    """Every gear's frame against the read's, to 1e-6: exactly for a gearbox built to turn (``exact`` None: as the
    record's kind says), modulo the gear's pitch for W4's static one."""
    box = desk.record.gearbox
    exact = turning(desk) if exact is None else exact
    names = [c.name for c in box.components] + [c.component for c in carriers_of(box)] + [box.layout_component]
    started = time.monotonic()
    live = run(worker, lambda s: live_frames(s, box.assembly, names))
    want = wanted(desk)
    for c in carriers_of(box):
        rotation, at, _ = want[wb_layout.carrier_id(c.shaft)]
        got = live[c.component]
        origin, off, residue = frame_error(got, (rotation, at), 0.0)
        check(swbuild.same_frame(got[0], got[1], rotation, at, 0.0),
              f"{label}: the carrier {c.shaft} ({c.component}) at {tuple(round(v, 9) for v in got[1])}, origin off "
              f"{origin:.1e} mm, turn off {off:.1e}° (exactly), axis off {residue:.1e}")
        check(swbuild.same_frame(c.rotation, c.at, rotation, at, 0.0),
              f"{label}: the carrier {c.shaft}'s frame on record is the one the workbook wants")
    for c in box.components:
        rotation, at, pitch = want[c.gear]
        got = live[c.name]
        origin, off, residue = frame_error(got, (rotation, at), 0.0 if exact else pitch)
        check(swbuild.same_frame(got[0], got[1], rotation, at, 0.0 if exact else pitch),
              f"{label}: {c.gear} ({c.name}) at {tuple(round(v, 9) for v in got[1])}, origin off {origin:.1e} mm, "
              f"turn off {off:.1e}°{' (exactly)' if exact else f' modulo its pitch {pitch:.4f}°'}, axis off "
              f"{residue:.1e}")
        check(swbuild.same_frame(c.rotation, c.at, rotation, at, 0.0 if exact else pitch),
              f"{label}: {c.gear}'s frame on record is the one the workbook wants")
    lay = live[box.layout_component]
    check(swbuild.same_frame(lay[0], lay[1], wb_layout.IDENTITY, (0.0, 0.0, 0.0)),
          f"{label}: the layout ({box.layout_component}) is at identity")
    say(f"        frames read in {time.monotonic() - started:.1f} s")
    return live


def axis_on_line(params, point, direction):
    """A layout axis read by ``GetRefAxisParams`` (two points, metres) against its shaft's line: (the farther point's
    distance from the line in mm, the axis's unit direction, its dot with the shaft's direction)."""
    p = [float(v) * 1000.0 for v in params[:3]]
    q = [float(v) * 1000.0 for v in params[3:6]]
    d = [b - a for a, b in zip(p, q)]
    n = math.sqrt(sum(c * c for c in d))
    if n == 0.0:
        return float("inf"), (0.0, 0.0, 0.0), 0.0
    u = tuple(c / n for c in d)
    w = [float(c) for c in direction]
    off = 0.0
    for x in (p, q):
        r = [x[i] - float(point[i]) for i in range(3)]
        cross = (r[1] * w[2] - r[2] * w[1], r[2] * w[0] - r[0] * w[2], r[0] * w[1] - r[1] * w[0])
        off = max(off, math.sqrt(sum(c * c for c in cross)))
    return off, u, sum(a * b for a, b in zip(u, w))


def measure_axes(worker, desk, label):
    """Each layout axis on its shaft's line to 1e-6 mm, along its direction either way (W6-PLAN §6.1), the sign
    logged; an axis of the Z family must also read +Z, as W4/W5 asserted (findings.LAYOUT_AXIS_Z_SIGN)."""
    box = desk.record.gearbox
    axes, values = run(worker, lambda s: live_axes(s, box.layout, [s_.axis_name for s_ in box.shafts]))
    say(f"        {os.path.basename(box.layout)} globals {values}")
    for shaft in desk.plan_shafts():
        off, u, dot = axis_on_line(axes[shaft.axis_name], (shaft.x, shaft.y, shaft.z), shaft.direction)
        z_family = abs(abs(float(shaft.direction[2])) - 1.0) < 1e-12
        check(off <= 1e-6 and abs(abs(dot) - 1.0) <= 1e-9 and (not z_family or u[2] > 1 - 1e-9),
              f"{label}: {shaft.axis_name} on {shaft.shaft}'s line through ({shaft.x:g}, {shaft.y:g}, {shaft.z:g}) "
              f"(off {off:.1e} mm), along {tuple(round(c, 9) for c in u)}, {'+' if dot > 0 else '-'} its Axis "
              f"{shaft.axis}{' (reads +Z)' if z_family else ''}")
        if not z_family:
            say(f"fact    {label}: {shaft.axis_name} reads {'along' if dot > 0 else 'against'} {shaft.shaft}'s Axis "
                f"{shaft.axis}")
    return axes


def measure_clear(worker, desk, label):
    found = run(worker, lambda s: live_interferences(s, desk.record.gearbox.assembly))
    check(found == [], f"{label}: no interference in {os.path.basename(desk.record.gearbox.assembly)}: {found}")


def measure_mates(worker, desk, label):
    """§4.1's mates: exactly the record's names and nothing else in the mate group, every code 0, none suppressed,
    every mated gear under-defined (2); the fixed gears' statuses logged."""
    box = desk.record.gearbox
    want = [m.name for m in box.mates]
    states, others, status = run(worker, lambda s: live_mates(s, box.assembly, bodies(box)))
    names = [s.name for s in states]
    say(f"        mates {[(s.name, s.code, s.warning, s.suppressed) for s in states]}; others {others}; "
        f"constrained {status}")
    check(sorted(names) == sorted(want), f"{label}: the mates are exactly the record's {len(want)}: extra "
          f"{sorted(set(names) - set(want))}, missing {sorted(set(want) - set(names))}")
    check(not others, f"{label}: nothing but mates in the mate group: {others}")
    bad = [(s.name, s.code, s.warning) for s in states if s.code]
    check(not bad, f"{label}: every mate's error code is 0: {bad}")
    off = [s.name for s in states if s.suppressed]
    check(not off, f"{label}: no mate suppressed: {off}")
    mated = [g for g, _ in bodies(box) if g not in box.fixed]
    loose = {g: status[g] for g in mated if status[g] != findings.COMPONENT_UNDER_DEFINED}
    check(not loose, f"{label}: every mated gear{' and carrier' if carriers_of(box) else ''} under-defined "
          f"({findings.COMPONENT_UNDER_DEFINED}): {status}")
    return states


def control_gear(box, a, b, count, locked):
    """The gear of mesh (a, b) a control turns, and the locks to suppress around it: W4's choice (b when it is in
    one mesh only, else a) unless that gear is in a lock; then the other, if it is in none; else W4's choice with
    every lock touching either gear suppressed (W5-PLAN §4.1: Risky_Placements' G3–G4)."""
    order = [b, a] if count[b] == 1 else [a, b]
    free = [g for g in order if g not in locked]
    if free:
        return free[0], []
    return order[0], [m.name for m in box.mates if m.kind == "lock" and (a in m.gears or b in m.gears)]


def negative_controls(worker, desk, label):
    """Every listed mesh: one of its gears turned half a pitch must clash with its partner and nothing else."""
    box = desk.record.gearbox
    name_of = {c.gear: c.name for c in box.components}
    gear_of = {c.name: c.gear for c in box.components}
    meshes = [tuple(m) for m in box.meshes]
    count = {c.gear: sum(c.gear in m for m in meshes) for c in box.components}
    moving = turning(desk)
    locked = {g for m in box.mates if m.kind == "lock" for g in m.gears} if moving else set()
    kind = swcom.ASSEMBLY_TRAIN if moving else swcom.ASSEMBLY_STATIC
    want = wanted(desk)
    for a, b in meshes:
        turned, locks = control_gear(box, a, b, count, locked)
        rotation, at, pitch = want[turned]
        started = time.monotonic()
        moved, back = run(worker, lambda s: placed_elsewhere(s, box.assembly, name_of[turned],
                                                              turn_about_z(rotation, pitch / 2), at, kind, locks))
        merged = swbuild._clashes(moved, gear_of)  # noqa: SLF001
        check(bool(merged) and all(set(c.gears) == {a, b} and c.volume > 0 for c in merged),
              f"{label}: {turned} turned half a pitch ({pitch / 2:.4f}°)"
              f"{f' with {locks} suppressed' if locks else ''}: {len(moved)} interference(s), merged "
              f"{[(c.gears, round(c.volume, 3)) for c in merged]}, all between {a} and {b}")
        check(back == [], f"{label}: {turned} put back, no interference ({time.monotonic() - started:.1f} s)")
    if moving:
        measure_frames(worker, desk, f"{label}, after the controls")
        measure_mates(worker, desk, f"{label}, after the controls")


def live_open(session, path):
    """The app's own open of a saved document (OpenDoc6 then ActivateDoc3), reading nothing else."""
    in_assembly(path, lambda s: None)(session)


def reopen(worker, desk, label):
    left = run(worker, close_ours)
    check(not left, f"{label}: saved and closed this run's documents: left {left}")
    say(f"        open now: {run(worker, open_titles)}")
    box = desk.record.gearbox
    paths = [box.assembly, box.layout] + sorted({c.part for c in box.components}) + [c.path for c in carriers_of(box)]
    # Read straight after the open, before any frame read (which read marks the assembly was never isolated).
    run(worker, lambda s: live_open(s, box.assembly))
    flags = run(worker, lambda s: save_flags(s, paths))
    check(len(flags) == len(paths) and not marked(flags),
          f"{label}, reopened: every document just opened from its file reads GetSaveFlag False (the record clears "
          f"a mark on that reading): {flags}")
    measure_frames(worker, desk, f"{label}, reopened")
    say(f"fact    {label}, reopened: marked modified after the frame reads (component_frame): "
        f"{marked(run(worker, lambda s: save_flags(s, paths)))}")
    if turning(desk):
        measure_mates(worker, desk, f"{label}, reopened")
        say(f"fact    {label}, reopened: marked modified after the mate reads (mate_states, GetConstrainedStatus): "
            f"{marked(run(worker, lambda s: save_flags(s, paths)))}")
    found = run(worker, lambda s: live_interferences(s, box.assembly))
    say(f"fact    {label}, reopened: marked modified after interferences() ({len(found)} found): "
        f"{marked(run(worker, lambda s: save_flags(s, paths)))}")


def measure(worker, desk, label, controls=True, again=True):
    """§4.1: frames, axes, interference, the mates (built to turn), the negative controls, and the reopen. W7: the
    carrier part's skeleton and axes, the held members fixed, and each copy's own half-pitch control."""
    say(f"measure {label}: {memory()}; turning {turning(desk)}")
    planetary = bool(carriers_of(desk.record.gearbox))
    live = measure_frames(worker, desk, label)
    measure_axes(worker, desk, label)
    if planetary:
        carrier_part_check(worker, desk, label, live)
        held_fixed(worker, desk, label)
    measure_clear(worker, desk, label)
    if turning(desk):
        measure_mates(worker, desk, label)
    if controls and planetary:
        copy_controls(worker, desk, label)
    elif controls:
        negative_controls(worker, desk, label)
    if again:
        reopen(worker, desk, label)


# -- §4.2: the drive, the user's turn, and what Update found -------------------------------------------------


# -- W6: a gear mate's sense, read raw and judged (W6-PLAN §6.1) ---------------------------------------------


def gear_axes(frames, a, b):
    """The two gears' own +Z as placed (each frame's third column), gear a first."""
    return tuple((float(frames[g][0][2]), float(frames[g][0][5]), float(frames[g][0][8])) for g in (a, b))


def axes_turned(axes):
    """Whether two own axes are of different families (planning's rule, |â × b̂| ≥ 1e-9): a turned mesh."""
    a, b = axes
    cross = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    return math.sqrt(sum(c * c for c in cross)) >= 1e-9


def mesh_same_sense(desk, a, b):
    """k > 0 for the mesh (a, b), from the read's kinematics alone: its two gears turn the same way about their own
    axes (speeds about each shaft's own axis, W5-DECISIONS M2) — the ``same_sense`` the app reads a gear mate
    against, worked out here without the app's record. W7: in the mesh's carrier's frame (relative speeds), which a
    gear mate on a carrier holds (W7-SPIKE.md)."""
    carrier = mesh_carrier(desk, a, b) if desk.a.report.layout.placed else ""
    return relative_speed(desk, a, carrier) * relative_speed(desk, b, carrier) > 0


def mate_read(session, handle, name, axes, same_sense, gears):
    """One gear mate read the way the app reads it (``Session.gear_mate_sense``; reading only, the definition
    released): its Reverse, each entity's direction and a point on it (``EntityParams``, assembly space), which gear
    each lies along (|d·g| >= swcom.ENTITY_ALONG) with its τ, rule H's verdict on those numbers
    (``swcom.sense_reading``) and the app's own verdict, or the sentence it refused with."""
    session.find_mate(handle, name)
    out = {"mate": name, "same": bool(same_sense), "axes": axes, "gears": tuple(gears)}
    try:
        _, feature = session._kept_mate(handle)  # noqa: SLF001
        data = swcom._read(feature, "GetDefinition")  # noqa: SLF001
        out["reverse"] = swcom._read(data, "Reverse") if data is not None else None  # noqa: SLF001
        data = None
        mate = swcom._read(feature, "GetSpecificFeature2")  # noqa: SLF001
        count = swcom._read(mate, "GetMateEntityCount") if mate is not None else None  # noqa: SLF001
        directions, entities = [], []
        for index in range(int(count) if isinstance(count, (int, float)) else 0):
            entity = call(mate, "MateEntity", index)
            params = swcom._read(entity, "EntityParams") if entity is not None else None  # noqa: SLF001
            values = [float(v) for v in params] if params is not None else []
            if len(values) < 6:
                continue
            d = tuple(values[3:6])
            along = [sum(x * y for x, y in zip(d, g)) for g in axes]
            which = next((i for i in (0, 1) if abs(along[i]) >= swcom.ENTITY_ALONG), None)
            directions.append(d)
            entities.append({"direction": tuple(round(v, 9) for v in d),
                             "point": tuple(round(v * 1000.0, 6) for v in values[0:3]),
                             "gear": gears[which] if which is not None else "neither",
                             "tau": (1 if along[which] > 0 else -1) if which is not None else 0})
        out["entities"] = entities
        out["rule"] = swcom.sense_reading(out["reverse"], directions, axes, same_sense, mate=name)
    except Exception as exc:  # noqa: BLE001 - logged beside the app's own read
        out["raw_error"] = f"{type(exc).__name__}: {exc}"
    try:
        out["app"] = session.gear_mate_sense(handle, bool(same_sense), axes)
    except Exception as exc:  # noqa: BLE001 - the app's refusal is its sentence
        out["app_error"] = f"{type(exc).__name__}: {exc}"
    return out


def say_read(label, read):
    """The read, logged. On parallel axes only the product τa·τb means anything (W6-INTERFACES §7.4): no single τ,
    and no entity matched to one gear, is named there."""
    turned = axes_turned(read["axes"])

    def verdict(found):
        if not isinstance(found, tuple):
            return found
        right, taus = found
        return f"right {right}, τ {tuple(taus)}" if turned else f"right {right}, τa·τb {taus[0] * taus[1]:+d}"
    entities = "; ".join(
        (f"entity {i + 1} along {e['gear']} τ {e['tau']:+d}, " if turned else f"entity {i + 1} ")
        + f"direction {e['direction']} through {e['point']} mm" for i, e in enumerate(read.get("entities", [])))
    say(f"read    {label}: {read['mate']}: Reverse {read.get('reverse')}; {entities or 'no entities read'}; k > 0 "
        f"{read['same']}; rule H {verdict(read.get('rule', read.get('raw_error')))}; the app "
        f"{verdict(read.get('app', read.get('app_error')))}; {'turned' if turned else 'parallel'} axes "
        f"{read['axes']}")


def mate_readings(worker, desk, label):
    """Every gear mate of the record read (``mate_read``), logged, and the app's verdict asserted right on each:
    straight after a build (whose sense read turned round any it read wrong), after an Update that made one again,
    after a reopen. The record's sense must agree with the read's kinematics (``mate_senses = (sense == -1)``)."""
    box = desk.record.gearbox
    frames = frames_on_record(desk)
    meshes = [m for m in box.mates if m.kind == "mesh"]
    for m in meshes:
        same = mesh_same_sense(desk, *m.gears)
        sense = int(getattr(m, "sense", 0) or 0)
        check(sense in (0, 1, -1) and (sense == 0 or (sense == -1) == same),
              f"{label}: {m.name}'s sense on record {sense} agrees with the kinematics (k > 0 {same})")

    def work(s):
        return [mate_read(s, f"r{i}", m.name, gear_axes(frames, *m.gears), mesh_same_sense(desk, *m.gears),
                          tuple(m.gears)) for i, m in enumerate(meshes)]
    reads = run(worker, in_assembly(box.assembly, work))
    for read in reads:
        say_read(label, read)
        app = read.get("app")
        check(app is not None and app[0] is True, f"{label}: the app reads {read['mate']} turning right "
              f"({'turned' if axes_turned(read['axes']) else 'parallel'} axes): {app or read.get('app_error')}")
        if app is not None and "rule" in read:
            same = (tuple(read["rule"][1]) == tuple(app[1]) if axes_turned(read["axes"])
                    else read["rule"][1][0] * read["rule"][1][1] == app[1][0] * app[1][1])
            check(read["rule"][0] == app[0] and same, f"{label}: rule H on the raw read agrees with the app's own "
                  f"read of {read['mate']}")
    return reads


def drive_job(asm, components, layout_name, input_gear, control=None, turn_by=None, fixed=(), phases=(),
              plane="plane3", clash_driven=False, mode="", configs=()):
    """One worker job on the assembly. The angle mate DRIVE_MATE from the input's Top plane to the layout's base plane
    ``plane`` (W5: Right; W6: the one square to the input's u₀) at 90°, its D1 linked to the global DRIVE. ``turn_by``
    None: DRIVE 90 -> 120 -> 90; then, given ``control`` (a dict: ``a``, ``b``, the recorded gear mate's name
    ``mesh``, its ``ratio``; W6: the gears' ``axes`` and the mesh's ``same`` sense, for the mate's read straight after
    it is made, and ``clash``, for the interference read at the driven position), that mate suppressed and CONTROL +
    name made in its place with each Flip in turn, driven 90 -> 120 -> 90, deleted, the recorded one turned back on. ``turn_by`` d (the user's turn):
    DRIVE 90 -> 90 + d and the drive taken away at once, leaving the train turned. Whatever happens, the cleanup
    runs in review M12's order — DRIVE set back (not for a user's turn) before the control mate is deleted; the
    recorded gear mate turned back on; the drive's equations deleted (last first) and the angle mate — each step
    on its own, its error kept. Returns every frame read and what was left.

    W8 (W8-PLAN §5), ``mode`` given: the configuration ``mode`` shown and the train rebuilt straight after the open,
    before any component is found (the handle rule), its name read back as ``active``; the recorded gear mate of a
    control suppressed and turned back on in ``mode`` only (``set_mate_suppressed_in``); and every mate's flag in
    every configuration of ``configs`` read after the cleanup (``flags_after``). The W8 spike saw ``IEquationMgr.Add2``
    refuse a dimension link (-1) once several configurations existed, so when the drive's link is refused there,
    the global is taken away again and DRIVE is moved by the angle mate's own value in ``mode``
    (``set_dimension_in``, ``findings.SLIDE_VALUE_ROUTE``'s call, given radians as SolidWorks' system unit);
    ``route`` says which drove it ("global" or "value")."""
    def job(session):
        out = {"errors": [], "cleanup": [], "rebuilds": []}
        made = {"global": False, "drive": "", "control": "", "suppressed": False, "at": DRIVE_FROM,
                "route": "global"}
        handle = {}

        def frames():
            return {g: session.component_frame(h) for g, h in handle.items()}

        def rebuild(what):
            out["rebuilds"].append((what, bool(session.rebuild(kind=swcom.ASSEMBLY_TRAIN))))

        def set_drive(value):
            if made["route"] == "value":
                session.set_dimension_in("ddrive", math.radians(value) * 1000.0, [mode])
            else:
                session.set_global_variable(DRIVE, f"{value:g}")
            made["at"] = value
            rebuild(f"{DRIVE} {value:g}")
            if made["route"] == "value":          # the review's watch: the angle as read back, and the input after
                read = session.dimension_values("ddrive", [mode])[mode]
                out.setdefault("route_reads", []).append(
                    (value, round(math.degrees(read / 1000.0), 9),
                     tuple(round(v, 9) for v in session.component_frame(handle[input_gear])[0][:2])))

        def drop_drive_equations():
            texts = [text for text, _ in session.equations()]
            for index in range(len(texts) - 1, -1, -1):
                if equations.quote(DRIVE) in texts[index]:
                    session.delete_equation(index)

        def attempt(what, action):
            try:
                action()
            except Exception as exc:  # noqa: BLE001 - kept, and the next cleanup step still runs
                out["cleanup"].append(f"{what}: {type(exc).__name__}: {exc}")

        session.begin_build()
        try:
            try:
                session.open_document(asm)
                if mode:
                    session.show_configuration(mode)
                    rebuild(f"{mode} shown")
                    out["active"] = session.active_configuration()
                for index, (gear, name) in enumerate(components):
                    session.find_component(f"d{index}", name)
                    handle[gear] = f"d{index}"
                session.find_component("dlay", layout_name)
                out["equations_before"] = [text for text, _ in session.equations()]
                out["mates_before"] = [s.name for s in session.mate_states()]
                out["built"] = frames()
                session.add_global_variable(DRIVE, f"{DRIVE_FROM:g}")
                made["global"] = True
                name, dim = session.add_mate("ddrive", "angle", f"{handle[input_gear]}:plane2", f"dlay:{plane}",
                                             DRIVE_FROM, DRIVE_MATE)
                made["drive"] = name
                out["drive_mate"] = (name, dim, session.mate_status(name))
                try:
                    session.link_dimension(f"{dim}@{name}", equations.quote(DRIVE))
                except swcom.SolidWorksError as exc:
                    if not mode:
                        raise
                    out["link_refused"] = f"{type(exc).__name__}: {exc}"
                    drop_drive_equations()
                    made["global"], made["route"] = False, "value"
                out["route"] = made["route"]
                rebuild("drive added")
                out["added"] = frames()
                out["states_added"] = [(s.name, s.code, s.warning, s.suppressed) for s in session.mate_states()]
                if turn_by is not None:
                    set_drive(DRIVE_FROM + turn_by)
                    out["turned"] = frames()
                else:
                    set_drive(DRIVE_TO)
                    out["driven"] = frames()
                    out["states_driven"] = [(s.name, s.code, s.warning, s.suppressed) for s in session.mate_states()]
                    if clash_driven:              # W7-PLAN §6 (review S11): the unmated meshes seen clearing
                        out["driven_clash"] = session.interferences()
                    set_drive(DRIVE_FROM)
                    out["back"] = frames()
                    for step in phases:               # the input turned on by ``step`` degrees: interference read
                        set_drive(DRIVE_FROM + step)
                        out.setdefault("phases", []).append((step, frames(), session.interferences()))
                    if phases:
                        set_drive(DRIVE_FROM)
                        out["back"] = frames()
                    if control:
                        a, b, mesh, ratio = control["a"], control["b"], control["mesh"], control["ratio"]
                        session.find_mate("dmesh", mesh)
                        if mode:
                            made["suppressed"] = True     # review N3: marked first, restored whatever the call answers
                            session.set_mate_suppressed_in("dmesh", True, [mode])
                        else:
                            session.set_mate_suppressed("dmesh", True)
                        made["suppressed"] = True
                        # Both Flips, one after the other: since the build turns round a gear mate it reads turning
                        # against its mesh (9afe65b), the recorded mate may hold either, so the control is the Flip
                        # that turns wrong, whichever that is; the other must turn right.
                        for flip in (not bool(findings.GEAR_MATE_FLIP), bool(findings.GEAR_MATE_FLIP)):
                            cname, _ = session.add_mate("dctl", "gear", f"{handle[a]}:Gear Axis",
                                                        f"{handle[b]}:Gear Axis", 0.0, CONTROL + mesh,
                                                        ratio=(float(ratio[0]), float(ratio[1])), flip=flip)
                            made["control"] = cname
                            out.setdefault("control_mate", []).append((flip, cname, session.mate_status(cname)))
                            if control.get("axes"):    # W6-PLAN §6.1: read straight after it is made, before a rebuild
                                out[f"control_read {flip}"] = mate_read(session, "dread", cname, control["axes"],
                                                                        control["same"], (a, b))
                            rebuild(f"control added, Flip {flip}")
                            out[f"control_added {flip}"] = frames()
                            set_drive(DRIVE_TO)
                            out[f"control_driven {flip}"] = frames()
                            if control.get("clash"):   # review M2: at the driven position, 30° off the built phase
                                out[f"control_clash {flip}"] = session.interferences()
                            set_drive(DRIVE_FROM)      # M12: Drive set back before the control mate is deleted
                            out[f"control_back {flip}"] = frames()
                            delete_mate(session, cname)
                            made["control"] = ""
                        out["control_back"] = out[f"control_back {bool(findings.GEAR_MATE_FLIP)}"]
            except Exception as exc:  # noqa: BLE001 - said, and the cleanup below still runs
                out["errors"].append(f"{type(exc).__name__}: {exc}")
                out["traceback"] = traceback.format_exc()
            # -- the cleanup, review M12's order
            if (made["global"] or (made["route"] == "value" and made["drive"])) and turn_by is None \
                    and made["at"] != DRIVE_FROM:
                attempt(f"{DRIVE} set back to {DRIVE_FROM:g}", lambda: set_drive(DRIVE_FROM))
            if made["control"]:
                def gone_control():
                    delete_mate(session, made["control"])
                    made["control"] = ""
                attempt("the control mate deleted", gone_control)
            if made["suppressed"]:
                def back_on():
                    if mode:
                        if session.mate_suppression("dmesh", [mode])[mode]:
                            session.set_mate_suppressed_in("dmesh", False, [mode])
                    else:
                        session.set_mate_suppressed("dmesh", False)
                    made["suppressed"] = False
                attempt("the recorded gear mate turned back on", back_on)
            if control and turn_by is None and "control_back" in out:
                attempt("rebuilt with the recorded gear mate back", lambda: rebuild("control gone"))
                attempt("frames read", lambda: out.__setitem__("control_gone", frames()))
            if made["global"]:
                attempt(f"the {DRIVE} equations deleted", drop_drive_equations)
            if made["drive"]:
                attempt("the angle mate deleted", lambda: delete_mate(session, made["drive"]))
            attempt("rebuilt with the drive gone", lambda: rebuild("drive gone"))
            attempt("the state read after", lambda: out.update(
                after=frames(), equations_after=[text for text, _ in session.equations()],
                states_after=[(s.name, s.code, s.warning, s.suppressed) for s in session.mate_states()],
                constrained_after={g: session.constrained_status(h) for g, h in handle.items() if g not in fixed}))
            if mode:
                def flags_after():
                    flags = {}
                    for index, name in enumerate(out.get("mates_before", [])):
                        session.find_mate(f"dflag{index}", name)
                        flags[name] = session.mate_suppression(f"dflag{index}", list(configs))
                    out["flags_after"] = flags
                attempt("every mate's flag read in every configuration", flags_after)
            return out
        finally:
            session.end_build()
    return job


def body_shaft(desk, body):
    """The Shafts row whose speed a body turns at: a gear's row's shaft (a planet copy's is its row's, ``P``), a
    carrier's own shaft (W7: its id is ``"<shaft> carrier"``)."""
    if body.endswith(wb_layout.CARRIER_ID_SUFFIX):
        return body[:-len(wb_layout.CARRIER_ID_SUFFIX)]
    placed = desk.a.report.layout.placed.get(body)
    row = placed.row if placed is not None and getattr(placed, "row", "") else body
    return next(g.shaft for g in desk.a.spec.gears if g.id == row)


def expected_turns(desk, gears, input_gear, step, sense=1):
    """δ_i = sense · step · ω_i / ω_in (W5-DECISIONS M2: speeds about each shaft's own axis), in degrees about each
    gear's own +Z; ``sense`` the sign the input was measured (or, W5, ruled) to turn by. W7: a planet copy turns at
    its row's shaft's own-axis speed in the origin's frame, a carrier at its shaft's."""
    speeds = desk.a.report.motion.speeds
    w_in = speeds[body_shaft(desk, input_gear)]
    return {g: sense * step * float(speeds[body_shaft(desk, g)] / w_in) for g in gears}


def carrier_of_body(desk, body):
    """The carrier a planet copy rides (its carrier id), or ""."""
    placed = desk.a.report.layout.placed.get(body)
    carrier = getattr(placed, "carrier", "") if placed is not None else ""
    return wb_layout.carrier_id(carrier) if carrier else ""


def rotate_about(point, origin, axis, degrees):
    """``point`` turned ``degrees`` right-handed about the line through ``origin`` along ``axis`` (Rodrigues)."""
    n = math.sqrt(sum(float(a) * float(a) for a in axis))
    k = [float(a) / n for a in axis]
    v = [float(point[i]) - float(origin[i]) for i in range(3)]
    c, s_ = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    cross = (k[1] * v[2] - k[2] * v[1], k[2] * v[0] - k[0] * v[2], k[0] * v[1] - k[1] * v[0])
    dot = sum(k[i] * v[i] for i in range(3))
    return tuple(float(origin[i]) + v[i] * c + cross[i] * s_ + k[i] * dot * (1 - c) for i in range(3))


def expected_frames(desk, built, turns):
    """Where every body should stand after it turned ``turns`` (degrees about its own +Z, by body id) from ``built``:
    each turned about its own axis; a planet copy's origin also carried round its carrier's axis by the carrier's
    turn (W7-PLAN §6: "every copy's origin carried to its place"). A gear on a carrier's own shaft and the carrier
    itself stay where they are, turned."""
    out = {}
    for body, (rotation, at) in built.items():
        new_at = tuple(at)
        carrier = carrier_of_body(desk, body)
        if carrier and carrier in built and carrier in turns:
            c_rot, c_at = built[carrier]
            axis = (float(c_rot[2]), float(c_rot[5]), float(c_rot[8]))
            new_at = rotate_about(at, c_at, axis, turns[carrier])
        out[body] = (turn_about_z(rotation, turns.get(body, 0.0)), new_at)
    return out


def relative_speed(desk, body, carrier_shaft):
    """A body's speed relative to a carrier, about the body's own axis: ``ω − s·ω_c``, s = ±1 as the body faces the
    carrier's way or not (W7-PLAN §2.5)."""
    speeds = desk.a.report.motion.speeds
    placed = desk.a.report.layout.placed
    w = float(speeds[body_shaft(desk, body)])
    if not carrier_shaft:
        return w
    axis_c = next(tuple(float(v) for v in c.direction) for c in carrier_layouts(desk) if c.shaft == carrier_shaft)
    axis_b = tuple(float(v) for v in placed[body].axis) if body in placed else axis_c
    s_ = 1.0 if sum(a * b for a, b in zip(axis_b, axis_c)) > 0 else -1.0
    return w - s_ * float(speeds[carrier_shaft])


def mesh_carrier(desk, a, b):
    """The carrier shaft a mesh turns in (W7), or "" on the frame."""
    placed = desk.a.report.layout.placed
    return (getattr(placed.get(a), "carrier", "") or getattr(placed.get(b), "carrier", "")) if placed else ""


def mesh_residuals(desk, built, after):
    """Every listed mesh at copy level (``geometry.expand_meshes``), mated or not, judged in step from the frames
    alone: each gear's turn relative to its mesh's carrier, δ_b − k·δ_a with k = −c·za/zb in that carrier's frame
    (W7-PLAN §2.5), in radians. Returns [(a, b, residual)]."""
    placed = desk.a.report.layout.placed
    out = []
    for a, b in wb_geometry.expand_meshes(desk.a.spec, placed):
        carrier = mesh_carrier(desk, a, b)
        cid = wb_layout.carrier_id(carrier) if carrier else ""
        dc = turn_degrees(built[cid][0], after[cid][0]) if cid else 0.0
        axis_c = next((tuple(float(v) for v in c.direction) for c in carrier_layouts(desk) if c.shaft == carrier),
                      (0.0, 0.0, 1.0))

        def rel(g):
            # A planet's rotation is its carrier's turn about the shared direction times its own, so for every gear
            # of the mesh, planet or frame gear alike, its turn relative to the carrier is δ − s·δ_c.
            turn = turn_degrees(built[g][0], after[g][0])
            if turn is None:
                return None
            s_ = 1.0 if sum(float(x) * y for x, y in zip(placed[g].axis, axis_c)) > 0 else -1.0
            return turn - s_ * dc
        ra, rb = rel(a), rel(b)
        if ra is None or rb is None:
            out.append((a, b, float("inf")))
            continue
        pa, pb = placed[a], placed[b]
        same = sum(float(x) * float(y) for x, y in zip(pa.axis, pb.axis)) > 0
        c = (1 if same else -1) * (-1 if (pa.internal != pb.internal) else 1)
        k = -c * pa.teeth / pb.teeth
        out.append((a, b, math.radians(rb - k * ra)))
    return out


def input_sense(label, turns, input_gear, step, ruled):
    """W6-PLAN §6.1: the input's turn is MEASURED, |δ_in| = ``step`` asserted (a miss stops the run); its sign is the
    one every other gear's expectation takes. ``ruled`` (a Z+ input, W5): the sign findings.DEMONSTRATION_DRIVE_SENSE
    says, which the measured one must equal."""
    measured = turns.get(input_gear)
    if measured is None or abs(abs(measured) - abs(step)) > DRIVE_TOLERANCE * abs(step):
        raise Halt(f"{label}: the drive turned the input {input_gear} {measured}°, not ±{abs(step):g}° (W6-PLAN §6.1: "
                   "stop and ask)")
    sign = 1 if measured * step > 0 else -1
    if ruled is not None and sign != ruled:
        raise Halt(f"{label}: the drive turned the input {input_gear} {measured:+.9f}° where "
                   f"DEMONSTRATION_DRIVE_SENSE says {ruled * step:+g}° (W5-PLAN §4.2: stop and ask)")
    say(f"fact    {label}: the input {input_gear} turned {measured:+.9f}° about its own +Z, measured"
        f"{' (as DEMONSTRATION_DRIVE_SENSE says for a Z+ input)' if ruled is not None else ''}")
    return sign


def say_turns(label, turns, expected):
    say(f"        {label}: " + ", ".join(f"{g} {turns[g]:+.9f}° (kinematics {expected[g]:+.9f}°)"
                                         if turns[g] is not None else f"{g} OFF ITS AXIS" for g in expected))


def close_turn(turn, expected):
    return turn is not None and abs(turn - expected) <= DRIVE_TOLERANCE * max(1.0, abs(expected))


def drive_inputs(desk):
    box = desk.record.gearbox
    components = bodies(box)                 # W7: each carrier too, by its carrier id
    gears = [g for g, _ in components]
    return box, components, gears, box.drag[0] if box.drag else ""


BASE_PLANES = (("plane3", "Right"), ("plane2", "Top"), ("plane1", "Front"))     # square to X, Y, Z


def drive_assumptions(desk, input_gear, label):
    """What the drive rests on (W5-PLAN §4.2, ruled on 2026-11-14; W6-PLAN §6.1), asserted before anything is added:
    a gear to drag; the input built at θ = 0 about its own axis (its Top plane, square to its own Y, then at 90° to
    the base plane square to its u₀ = own X: Right for a Z or Y input, Top for an X input); on a Z+ input
    findings.DEMONSTRATION_DRIVE_SENSE 1 (the sense probe demonstration_drive measured there, which the measured turn
    must then equal). Returns (the layout's plane, the ruled sign or None). A gearbox that breaks one stops the run
    with the sentence, rather than drive from an angle no probe measured."""
    if not input_gear:
        raise Halt(f"{label}: the record names no gear to drag, so the drive has no input")
    rotation = wanted(desk)[input_gear][0]
    placed = desk.a.report.layout.placed[input_gear]
    axis = tuple(float(c) for c in placed.axis)
    theta = turn_degrees(wb_geometry.base_frame(axis), rotation)
    if theta is None or abs(theta) > 1e-9:
        raise Halt(f"{label}: the drive is made at 90° from an input built at θ = 0; {input_gear} on {placed.shaft} "
                   f"is at {theta}° about its axis {axis}, so it is not driven")
    u0 = (float(rotation[0]), float(rotation[3]), float(rotation[6]))
    k = max(range(3), key=lambda i: abs(u0[i]))
    if abs(abs(u0[k]) - 1.0) > 1e-12:
        raise Halt(f"{label}: {input_gear}'s u₀ {u0} is square to no base plane, so no drive is made")
    plane, word = BASE_PLANES[k]
    ruled = None
    if axis == (0.0, 0.0, 1.0):
        if findings.DEMONSTRATION_DRIVE_SENSE != 1:
            raise Halt(f"{label}: findings.DEMONSTRATION_DRIVE_SENSE is {findings.DEMONSTRATION_DRIVE_SENSE!r}, not "
                       "the 1 this drive's expectations were ruled on")
        ruled = 1
    check(True, f"{label}: the drive's assumptions hold: {input_gear} on {placed.shaft} {axis} at θ = 0, u₀ {u0}, "
                f"its Top plane against the layout's {word} ({plane}); the input's turn "
                f"{'ruled by DEMONSTRATION_DRIVE_SENSE 1 and measured' if ruled else 'measured'}; tolerance "
                f"{DRIVE_TOLERANCE:g} relative")
    return plane, ruled


def drive_proof(worker, desk, label, control=None, phases=()):
    """§4.2 on the current assembly, which must stand at its built turn with the input at θ = 0. ``control``: the
    (a, b) of the recorded gear mate to flip for the wrong-sense control, or None. W6 (W6-PLAN §6.1): the input's
    turn measured; the control mate read straight after each Flip is made; on a turned mesh (axes not parallel), the
    interference judge after each control drive (review M2): the Flip the drive calls right clear, the other clashing
    with the mesh's partner only — a failure STOPS the run."""
    box, components, gears, input_gear = drive_inputs(desk)
    say(f"drive   {label}: input {input_gear}; control {control}; {memory()}")
    plane, ruled = drive_assumptions(desk, input_gear, label)
    mesh_entry, spec = None, None
    if control is not None:
        mesh_entry = next(m for m in box.mates if m.kind == "mesh" and tuple(m.gears) == tuple(control))
        a, b = mesh_entry.gears
        axes = gear_axes(frames_on_record(desk), a, b)
        spec = {"a": a, "b": b, "mesh": mesh_entry.name, "ratio": tuple(mesh_entry.ratio), "axes": axes,
                "same": mesh_same_sense(desk, a, b), "clash": True, "turned": axes_turned(axes)}
    started = time.monotonic()
    planetary = bool(carriers_of(box))
    if spec is not None and planetary:
        spec.update(turned=True, judge="any")    # W7: the whole train is the comparison, any clash the wrong Flip's
    out = run(worker, drive_job(box.assembly, components, box.layout_component, input_gear, control=spec,
                                fixed=box.fixed, phases=phases, plane=plane, clash_driven=planetary))
    gear_of = {c.name: c.gear for c in box.components}
    for step, _frames, found in out.get("phases", []):
        merged = swbuild._clashes(found, gear_of)  # noqa: SLF001
        say(f"fact    {label}: the input turned on {step:.4f}°: interference {len(found)} place(s), "
            f"{[(c.gears, round(c.volume, 6)) for c in merged]}")
        if planetary:
            check(not merged, f"{label}: the input turned on {step:.4f}°: no interference on any mesh, the unmated "
                  "ring meshes included")
    say(f"        in {time.monotonic() - started:.1f} s; rebuilds {out['rebuilds']}; drive mate "
        f"{out.get('drive_mate')}; control mate {out.get('control_mate')}")
    for line in out.get("traceback", "").splitlines():
        say("        " + line)
    check(not out["errors"], f"{label}: the drive ran without a raise: {out['errors']}")
    check(not out["cleanup"], f"{label}: every cleanup step ran: {out['cleanup']}")
    built = out.get("built")
    if built is None:
        raise Halt(f"{label}: the drive could not even read the built frames: {out['errors']}")
    record_frames = frames_on_record(desk)
    gap, at = frames_gap(built, record_frames)
    check(gap <= FRAME_TOLERANCE, f"{label}: before the drive every gear stands at its frame on record (largest "
          f"{gap:.1e} at {at or '-'})")
    if "added" not in out:
        raise Halt(f"{label}: the 90° drive could not be added: {out['errors']}")
    gap, at = frames_gap(out["added"], built)
    say(f"        states with the drive added: {out.get('states_added')}")
    if gap > FRAME_TOLERANCE:
        raise Halt(f"{label}: adding the 90° drive moved {at} by {gap:.1e} (W5-PLAN §4.2: stop and ask)")
    check(True, f"{label}: adding the 90° drive moved nothing (largest {gap:.1e})")
    step = DRIVE_TO - DRIVE_FROM
    expected = expected_turns(desk, gears, input_gear, step, 1 if ruled is None else ruled)
    if "driven" in out:
        turns = {g: turn_degrees(built[g][0], out["driven"][g][0]) for g in gears}
        sense = input_sense(label, turns, input_gear, step, ruled)
        expected = expected_turns(desk, gears, input_gear, step, sense)
        say_turns(f"{DRIVE} {DRIVE_FROM:g} -> {DRIVE_TO:g}", turns, expected)
        for g in gears:
            check(close_turn(turns[g], expected[g]),
                  f"{label}: {g} turned {turns[g] if turns[g] is None else f'{turns[g]:+.9f}'}° for "
                  f"{expected[g]:+.9f}°, sign included (off "
                  f"{'-' if turns[g] is None else f'{abs(turns[g] - expected[g]):.1e}'})")
        if planetary:
            want = expected_frames(desk, built, expected)
            gaps = {g: frame_gap(out["driven"][g], want[g]) for g in gears}
            check(all(v <= FRAME_TOLERANCE for v in gaps.values()),
                  f"{label}: driven, every body where the kinematics put it — each copy's origin carried round its "
                  f"carrier, the held member unmoved: { {g: f'{v:.1e}' for g, v in gaps.items()} }")
            for g in gears:
                if carrier_of_body(desk, g):
                    say(f"        {g} carried to {tuple(round(v, 6) for v in out['driven'][g][1])}")
            residuals = mesh_residuals(desk, built, out["driven"])
            check(all(abs(r) <= 1e-6 for _, _, r in residuals), f"{label}: every listed mesh in step, the unmated "
                  f"ones included: {[(a, b, f'{r:.1e} rad') for a, b, r in residuals]}")
            clash = out.get("driven_clash")
            merged = swbuild._clashes(clash or [], {n: g for g, n in components})  # noqa: SLF001
            check(clash is not None and not merged, f"{label}: interferences() with {DRIVE} at {DRIVE_TO:g}: none, "
                  f"every mesh, mated or not, clear: {[(c.gears, round(c.volume, 6)) for c in merged]}")
        else:
            moved = {g: frame_error(out["driven"][g], built[g], 0.0) for g in gears}
            check(all(o <= FRAME_TOLERANCE and r <= FRAME_TOLERANCE for o, _, r in moved.values()),
                  f"{label}: driven, every gear stays on its axis and in its place: "
                  f"{ {g: (f'{o:.1e}', f'{r:.1e}') for g, (o, _, r) in moved.items()} }")
        say(f"        states driven: {out.get('states_driven')}")
        check(not [s for s in out.get("states_driven", []) if s[1]], f"{label}: no mate in error while driven")
    if "back" in out:
        gap, at = frames_gap(out["back"], built)
        check(gap <= FRAME_TOLERANCE, f"{label}: {DRIVE} set back to {DRIVE_FROM:g}, every gear at its built frame "
              f"(largest {gap:.1e} at {at or '-'})")
    halt = ""
    if mesh_entry is not None:
        a, b = mesh_entry.gears
        flips = [f for f in (True, False) if f"control_driven {f}" in out]
        wrong, right = [], []
        if len(flips) == 2:
            for flip in flips:
                gap, at = frames_gap(out[f"control_added {flip}"], built)
                check(gap <= FRAME_TOLERANCE, f"{label}, control: the gear mate with Flip {flip} moved nothing when "
                      f"made (largest {gap:.1e})")
                turns = {g: turn_degrees(built[g][0], out[f"control_driven {flip}"][g][0]) for g in gears}
                say_turns(f"control, {CONTROL + mesh_entry.name} with Flip {flip}", turns, expected)
                if planetary:
                    # W7: a planetary's gear mates close a loop, so a wrong Flip turns the whole train wrong (the
                    # spike: carrier −15° where +7.5° is right): right is every body as the kinematics say.
                    want = expected_frames(desk, built, expected)
                    gap = max(frame_gap(out[f"control_driven {flip}"][g], want[g]) for g in gears)
                    if gap <= FRAME_TOLERANCE:
                        right.append(flip)
                    elif gap > 1e-3:
                        wrong.append(flip)
                        # A wrong Flip can land every gear a whole pitch from its right place (p7: the ring at +10°
                        # where −10° is right, 20° = 3 pitches of 54 teeth): its teeth then stand where the right
                        # ones would, and there is nothing for interference to see.
                        pitches = {g: wanted(desk)[g][2] if g in wanted(desk) else 0.0 for g in gears}
                        whole = True
                        for g in gears:
                            off = turns[g] - expected[g] if turns[g] is not None else float("inf")
                            p_ = pitches[g]
                            rem = min(off % p_, p_ - off % p_) if p_ else abs(off)
                            far = max(abs(float(x) - float(y)) for x, y in zip(out[f"control_driven {flip}"][g][1],
                                                                                 want[g][1]))
                            whole = whole and rem <= 1e-6 and far <= FRAME_TOLERANCE
                        if whole:
                            spec.setdefault("whole", []).append(flip)
                            say(f"fact    {label}, control: with Flip {flip} every body stands a whole number of its "
                                f"own pitches from its right place: {({g: round(turns[g] - expected[g], 6) for g in gears})}")
                    say(f"        control with Flip {flip}: largest frame off the kinematics {gap:.1e}")
                else:
                    if (turns[b] is not None and not close_turn(turns[b], expected[b])
                            and close_turn(turns[b], -expected[b]) and abs(expected[b]) > 1e-3):
                        wrong.append(flip)
                    elif close_turn(turns[b], expected[b]):
                        right.append(flip)
                    check(close_turn(turns[a], expected[a]), f"{label}, control: {a}, before the mesh, still turns "
                          f"{expected[a]:+.9f}° with Flip {flip} ({turns[a]})")
                gap, at = frames_gap(out[f"control_back {flip}"], built)
                check(gap <= FRAME_TOLERANCE, f"{label}, control: {DRIVE} set back with Flip {flip}'s mate on: every "
                      f"gear at its built frame (largest {gap:.1e} at {at or '-'})")
            check(len(wrong) == 1 and len(right) == 1,
                  f"{label}, control: a wrong sense is seen: with Flip {wrong} "
                  + ("the train turns off the kinematics" if planetary else f"{b} turns the mirror of the right turn")
                  + f", with Flip {right} it turns right (the comparison tells one from the other)")
            say(f"fact    {label}: {mesh_entry.name} turns right with Flip {right} here on SolidWorks "
                f"{TAG['version'] or TAG['major']} (findings.GEAR_MATE_FLIP {findings.GEAR_MATE_FLIP}; "
                f"{'a planetary train' if planetary else 'turned axes' if spec['turned'] else 'parallel axes'})")
            turned = mesh_entry.name in TURNED.get(os.path.normcase(box.assembly), set())
            left_on = [not bool(findings.GEAR_MATE_FLIP)] if turned else [bool(findings.GEAR_MATE_FLIP)]
            if not moved_since_made(desk, mesh_entry):
                check(right == left_on, f"{label}, control: the Flip that turns right, {right}, is the one SolidWorks "
                      f"made {mesh_entry.name} with ({left_on}: {'turned round' if turned else 'as first made'}); "
                      "neither gear has moved since")
            else:
                say(f"fact    {label}, control: a gear of {mesh_entry.name} has moved since the mate was made; a fresh "
                    f"mate turns right with Flip {right}, the recorded one was made with {left_on} "
                    f"({'turned round' if turned else 'as first made'}) and its own drive is judged above")
            for flip in flips:
                read = out.get(f"control_read {flip}")
                if read is not None:
                    say_read(f"{label}, control with Flip {flip}", read)
                    app = read.get("app")
                    if app is not None and len(right) == 1 and len(wrong) == 1:
                        check(bool(app[0]) == (flip in right), f"{label}, control: the app's read of the mate with "
                              f"Flip {flip} says right {app[0]}; the drive says {flip in right}")
            halt = clash_judge(out, label, spec, right, wrong, gear_of)
        else:
            check(False, f"{label}, control: never driven with both Flips: {out['errors']}")
            if spec["turned"]:
                halt = f"{label}, control: the turned mesh {mesh_entry.name} was never driven with both Flips"
        for key, what in (("control_gone", "the control mates deleted and the recorded one back on"),):
            if key in out:
                gap, at = frames_gap(out[key], built)
                check(gap <= FRAME_TOLERANCE, f"{label}, control: {what}: every gear at its built frame (largest "
                      f"{gap:.1e} at {at or '-'})")
    # M12, before anything is saved
    if "after" in out:
        gap, at = frames_gap(out["after"], built)
        check(gap <= FRAME_TOLERANCE, f"{label}: the drive gone, every frame against the built frames (largest "
              f"{gap:.1e} at {at or '-'})")
        check(out["equations_after"] == out["equations_before"] and not any(
            equations.quote(DRIVE) in t for t in out["equations_after"]),
              f"{label}: no {DRIVE} equation left: {[t for t in out['equations_after'] if t not in out['equations_before']]}")
        names = [s[0] for s in out["states_after"]]
        check(names == out["mates_before"] and DRIVE_MATE not in names and not any(n.startswith(CONTROL)
                                                                                   for n in names),
              f"{label}: no angle mate or control mate left; the mates as before: {names}")
        check(not [s for s in out["states_after"] if s[3]], f"{label}: no mate (no lock) left suppressed")
        check(not [s for s in out["states_after"] if s[1]], f"{label}: no mate in error after the drive")
        check(all(v == findings.COMPONENT_UNDER_DEFINED for v in out["constrained_after"].values()),
              f"{label}: every mated gear under-defined again: {out['constrained_after']}")
    else:
        check(False, f"{label}: the state after the drive could not be read: {out['cleanup']}")
    if halt:
        if planetary:          # W7: a section that fails logs FAIL and the run goes on (the coordinator, W7)
            check(False, halt)
        else:
            raise Halt(halt)
    return out


def clash_judge(out, label, spec, right, wrong, gear_of):
    """Review M2's interference check after each control drive: logged on any mesh; on a turned one, the Flip the
    drive calls right must show no interference at the driven position and the other must clash with the mesh's
    partner and nothing else. Returns the sentence that stops the run, or ""."""
    a, b, mesh = spec["a"], spec["b"], spec["mesh"]
    halt = []
    for flip in (True, False):
        found = out.get(f"control_clash {flip}")
        if found is None:
            if spec["turned"]:
                halt.append(f"no interference read with Flip {flip}")
            continue
        merged = swbuild._clashes(found, gear_of)  # noqa: SLF001
        said = [(c.gears, round(c.volume, 6)) for c in merged]
        say(f"fact    {label}, control: driven {DRIVE_TO - DRIVE_FROM:g}° with Flip {flip} "
            f"({'right' if flip in right else 'wrong' if flip in wrong else 'neither'}): interference {said}")
        if not spec["turned"]:
            continue
        if flip in right:
            ok = merged == []
            check(ok, f"{label}, control: with the Flip that turns right ({flip}) {mesh} runs clear: {said}")
            if not ok:
                halt.append(f"the right Flip {flip} clashes: {said}")
        elif flip in wrong and spec.get("judge") == "any" and flip in spec.get("whole", ()) and not merged:
            say(f"fact    {label}, control: the wrong Flip ({flip}) puts every gear a whole pitch off, so no clash can "
                "show it; the drive's frames told it wrong")
        elif flip in wrong and spec.get("judge") == "any":
            ok = bool(merged) and all(c.volume > 0 for c in merged)
            check(ok, f"{label}, control: with the wrong Flip ({flip}) the train clashes: {said}")
            if not ok:
                halt.append(f"the wrong Flip {flip} clashes nothing: {said}")
        elif flip in wrong:
            ok = bool(merged) and all(set(c.gears) == {a, b} and c.volume > 0 for c in merged)
            check(ok, f"{label}, control: with the wrong Flip ({flip}) {a} and {b} clash, and nothing else: {said}")
            if not ok:
                halt.append(f"the wrong Flip {flip} does not clash {a} with {b} alone: {said}")
        else:
            halt.append(f"Flip {flip} turns {b} neither right nor wrong")
    if spec["turned"] and (len(right) != 1 or len(wrong) != 1):
        halt.append(f"the drive told no right Flip from a wrong one (right {right}, wrong {wrong})")
    if halt:
        return (f"{label}: the interference check on the turned mesh {mesh} failed (review M2: stop): "
                + "; ".join(halt))
    return ""


def user_turn(worker, desk, label, degrees):
    """The user's turn, simulated (W5-PLAN §4.3): driven ``degrees`` and the drive deleted, as a hand drag leaves
    the train — every gear turned consistently. Returns the frames it left."""
    box, components, gears, input_gear = drive_inputs(desk)
    say(f"turn    {label}: {input_gear} by {degrees:g}° and the drive deleted")
    plane, ruled = drive_assumptions(desk, input_gear, label)
    out = run(worker, drive_job(box.assembly, components, box.layout_component, input_gear, turn_by=degrees,
                                fixed=box.fixed, plane=plane))
    say(f"        rebuilds {out['rebuilds']}")
    check(not out["errors"] and not out["cleanup"], f"{label}: turned and the drive deleted: {out['errors']} "
          f"{out['cleanup']}")
    if "after" not in out or "built" not in out or "added" not in out:
        raise Halt(f"{label}: the user's turn left no frames to read: {out['errors']} {out['cleanup']}")
    gap, at = frames_gap(out["added"], out["built"])
    if gap > FRAME_TOLERANCE:
        raise Halt(f"{label}: adding the 90° drive moved {at} by {gap:.1e} (W5-PLAN §4.2: stop and ask)")
    turns = {g: turn_degrees(out["built"][g][0], out["after"][g][0]) for g in gears}
    sense = input_sense(label, turns, input_gear, degrees, ruled)
    expected = expected_turns(desk, gears, input_gear, degrees, sense)
    say_turns("left turned", turns, expected)
    check(all(close_turn(turns[g], expected[g]) for g in gears), f"{label}: every gear left turned as the "
          "kinematics say")
    if carriers_of(box):
        want = expected_frames(desk, out["built"], expected)
        gap, at = frames_gap(out["after"], want)
        check(gap <= FRAME_TOLERANCE, f"{label}: every copy left carried round its carrier, every frame where the "
              f"kinematics put it (largest {gap:.1e} at {at or '-'})")
    check(not any(equations.quote(DRIVE) in t for t in out.get("equations_after", [])) and DRIVE_MATE not in
          [s[0] for s in out.get("states_after", [])], f"{label}: no drive left")
    links = desk.update.motion if desk.update is not None else None
    if links is not None:
        record_frames = frames_on_record(desk)
        pitch = {p.gear: p.pitch for p in links.recorded}
        held = list(getattr(links, "held", ()) or ())
        mated = [g for g in gears if g not in box.fixed or g in held]
        tc = swbuild.train_check({g: out["after"][g] for g in mated}, {g: record_frames[g] for g in mated},
                                 links.meshes, links.locks, pitch, carriers=getattr(links, "carriers", ()),
                                 held=held)
        say(f"        train_check after the turn: in step {tc.in_step}, turned {tc.turned}, off axis {tc.off_axis}, "
            f"out of step {tc.out_of_step}, residuals {[(a, b, f'{r:.2e}') for a, b, r in tc.residuals]}")
        check(tc.in_step and tc.turned, f"{label}: train_check reads the train in step and turned")
    return out["after"]


def say_found(result, recorded, label):
    """Each gear's origin, axis and turn residuals as Update found it (``result.found``, read before anything moved)
    against the frames on record before the press (``recorded``)."""
    for gear, (rotation, at) in recorded.items():
        found = result.found.get(gear)
        if found is None:
            say(f"        {label}: {gear} not read")
            continue
        origin, _, residue = frame_error(found, (rotation, at), 0.0)
        say(f"        {label}: {gear} found with its origin off {origin:.2e} mm and its axis off {residue:.2e}, "
            f"turned {turn_degrees(rotation, found[0])}° from its frame on record")


def update_marks(worker, desk, result, label, folder):
    paths = [os.path.join(folder, n) for n in os.listdir(folder) if n.upper().endswith((".SLDPRT", ".SLDASM"))]
    flags = run(worker, lambda s: save_flags(s, paths))
    say(f"        marked modified in SolidWorks right after the update: {flags}")
    check_marks(flags, expected_marks(result, desk.record.gearbox.assembly), label)


def all_mated(desk):
    box = desk.record.gearbox
    return sorted(c.gear for c in box.components if c.gear not in box.fixed)


def gearbox_flags(worker, desk):
    box = desk.record.gearbox
    paths = [box.assembly, box.layout] + sorted({c.part for c in box.components}) + [c.path for c in carriers_of(box)]
    return run(worker, lambda s: save_flags(s, paths))


def gear_frames(worker, desk):
    """Every gear's live frame, by gear id, read from SolidWorks."""
    box = desk.record.gearbox
    pairs = bodies(box)
    live = run(worker, lambda s: live_frames(s, box.assembly, [n for _, n in pairs]))
    return {g: live[n] for g, n in pairs}


def check_quiet_update(worker, desk, result, label, frames_before, flags_before):
    """An Update whose result changed nothing: read from SolidWorks, not from the app's result, every gear stands
    exactly where it stood before the press, and — findings.GEAR_MATE_DEFINITION_READ_MARKS is "nothing" — every
    document of the gearbox reads GetSaveFlag False before and after it (asserted, review of the run, 2026-11-14).
    An Update that did change something is said so and not judged here."""
    if result.changed or result.placed:
        say(f"fact    {label}: not an Update with nothing to do (changed "
            f"{[os.path.basename(p) for p in result.changed]}, placed {result.placed}): its frames and marks are "
            "judged as a change, not here")
        return
    after = gear_frames(worker, desk)
    gap, at = frames_gap(after, frames_before)
    check(gap <= FRAME_TOLERANCE, f"{label}: read from SolidWorks, every gear stands where it stood before the press "
          f"(largest {gap:.1e} at {at or '-'})")
    flags_after = gearbox_flags(worker, desk)
    say(f"fact    {label}: GetSaveFlag before the press {flags_before}, after it {flags_after}")
    check(flags_before and not marked(flags_before) and flags_after and not marked(flags_after),
          f"{label}: every document reads GetSaveFlag False before and after an Update that changed nothing "
          f"(GEAR_MATE_DEFINITION_READ_MARKS {getattr(findings, 'GEAR_MATE_DEFINITION_READ_MARKS', None)!r}): "
          f"marked before {marked(flags_before)}, after {marked(flags_after)}")


def update_nothing_turned(worker, desk, label, folder):
    """Update pressed with nothing changed on a train the user turned: no put, nothing changed, the sentence; and,
    read from SolidWorks, the train left exactly as turned and nothing marked."""
    desk.say_update()
    desk.say_footer(f"{label}, before the press")
    recorded = frames_on_record(desk)
    frames_before = gear_frames(worker, desk)
    flags_before = gearbox_flags(worker, desk)
    guard()
    _, result, _ = desk.update_solidworks()
    if result is None:
        return check(False, f"{label}: Update refused: {desk.note[0]}")
    say_found(result, recorded, label)
    check(result.ok and result.placed == [] and result.turned and not result.restored and result.changed == [],
          f"{label}: nothing put, nothing changed, the train found turned: placed {result.placed}, turned "
          f"{result.turned}, restored {result.restored}, changed {[os.path.basename(p) for p in result.changed]}")
    check_quiet_update(worker, desk, result, label, frames_before, flags_before)
    check(desk.record.unsaved == {}, f"{label}: the record marks nothing unsaved: {list(desk.record.unsaved)}")
    check(TURNED_SENTENCE in desk.note[0], f"{label}: the sentence ends {TURNED_SENTENCE!r}")
    desk.say_footer(f"{label}, after the press")
    return result


# -- Excel ----------------------------------------------------------------------------------------------------


OPEN_BOOKS = []            # every Workbook opened and not yet closed, so main closes what a section left open


class Workbook:
    """One workbook open in this run's own Excel."""

    def __init__(self, excel, path, tag):
        self.path = path
        self.wb, report = excel.open(path, tag)
        if self.wb is not None:
            OPEN_BOOKS.append(self)
        check(self.wb is not None and not report["repaired"],
              f"Excel opened {os.path.basename(path)} with no dialog or repair: {report.get('dialogs')}")

    def set(self, sheet, ref, value):
        cell = self.wb.Worksheets(sheet).Range(ref)
        if value is None:
            cell.ClearContents()
        elif isinstance(value, str) and value.startswith("="):
            cell.Formula = value
        else:
            cell.Value = value
        say(f"excel   {sheet}!{ref} := {value!r}")

    def get(self, sheet, ref):
        return self.wb.Worksheets(sheet).Range(ref).Value

    def save(self):
        self.wb.Save()
        say(f"excel   saved {os.path.basename(self.path)}")

    def close(self):
        self.wb.Close(SaveChanges=False)
        self.wb = None
        if self in OPEN_BOOKS:
            OPEN_BOOKS.remove(self)


def close_books():
    """Close, unsaved, every workbook a section left open (Excel keeps one workbook per file name, so the next
    section could not open its own beside it). Returns the names closed."""
    closed = []
    for book in list(OPEN_BOOKS):
        try:
            book.close()
            closed.append(os.path.basename(book.path))
        except Exception as exc:  # noqa: BLE001 - logged; the next section's own open check says what follows
            say(f"excel   could not close {os.path.basename(book.path)}: {exc}")
            if book in OPEN_BOOKS:
                OPEN_BOOKS.remove(book)
    return closed


def fresh_folder(name):
    folder = os.path.join(OUT, name)
    if os.path.exists(folder):
        raise SystemExit(f"{folder} exists already; give a fresh output folder")
    os.makedirs(folder)
    return folder


def fixture_desk(worker, excel, section, fixture):
    """A fixture copied into the section's folder, its Output folder set in Excel, read and planned."""
    folder = fresh_folder(section)
    path = os.path.join(folder, os.path.basename(fixture))
    shutil.copy2(fixture, path)
    book = Workbook(excel, path, section)
    book.set("Box", "B4", folder + "\\")
    book.save()
    desk = Desk(path, worker)
    desk.read()
    check(desk.a.lay_out_refusal() == "", "the gate is \"\"")
    return folder, path, book, desk


# The gear mates a fresh build on SolidWorks 2026 makes with Flip False, reads turning against their mesh and makes
# again with the other Flip (probe ring_mate_sense; 9afe65b): the Risky ring's mesh. Asserted on 2026 (major 34),
# logged on other versions.
RING_TURNED_ROUND = ("G5 meshes G6",)
# Per assembly path, the gear mates SolidWorks holds with the Flip other than findings.GEAR_MATE_FLIP: those a build
# turned round, kept up to date by every Update (a remade mate starts from GEAR_MATE_FLIP again unless that Update
# turned it round). The both-Flips control asserts that the Flip turning right is the one this says.
TURNED = {}
# Per (assembly path, gear mate name), the frames on record of the mate's two gears when SolidWorks last made it: a
# fresh gear mate's sense on SolidWorks 2024 depends on where its gears sit when it is made (m7, 2026-11-14), so the
# control's "the Flip that turns right is the one the build left" is asserted only while neither gear has moved since.
MADE_AT = {}


def note_made(desk, names):
    """Record where the gears of each gear mate in ``names`` stand on record now, as made there."""
    box = desk.record.gearbox
    frames = {c.gear: (tuple(c.rotation), tuple(c.at)) for c in box.components}
    for mate in box.mates:
        if mate.kind == "mesh" and mate.name in names:
            MADE_AT[(os.path.normcase(box.assembly), mate.name)] = {g: frames[g] for g in mate.gears}


def moved_since_made(desk, mate):
    """Whether a gear of ``mate`` stands elsewhere on record than when SolidWorks last made the mate (unknown: True)."""
    box = desk.record.gearbox
    made = MADE_AT.get((os.path.normcase(box.assembly), mate.name))
    if made is None:
        return True
    frames = {c.gear: (tuple(c.rotation), tuple(c.at)) for c in box.components}
    return any(frame_gap(frames[g], made[g]) > FRAME_TOLERANCE for g in mate.gears)


def build_turning(worker, desk, label, parts, turned_round=()):
    """Build, and the checks every turning build gets before §4.1: saved, turning, no interference, the marks, the
    footer with the drag instruction."""
    desk.say_footer(f"{label}, read")
    desk.say_plan()
    check(desk.plan is not None and desk.plan.motion is not None and not desk.plan.static_reason,
          f"{label}: the plan turns (W5): static reason {desk.plan.static_reason if desk.plan else None!r}")
    guard()
    plan, result = desk.build()
    if result is None:
        raise AssertionError(f"{label}: the build was refused: {desk.note[0]}")
    check(result.ok and result.kind == store.GEARBOX_MOTION and (parts is None or len(result.parts.built) == parts),
          f"{label}: {'every' if parts is None else parts} part(s), the layout part and the assembly built and saved, "
          f"turning: ok {result.ok}, parts built {len(result.parts.built)}, kind {result.kind!r}")
    check(result.clashes == [] and not result.interference_error, f"{label}: no interference: {result.clashes}")
    got = list(getattr(result.assembly, "turned_round", []) or [])
    TURNED[os.path.normcase(desk.record.gearbox.assembly)] = set(got)
    note_made(desk, [m.name for m in desk.record.gearbox.mates if m.kind == "mesh"])
    if turned_round is None:
        say(f"fact    {label}: the build's sense read made again with the other Flip: {got}")
    elif TAG["major"] == 34:
        check(got == list(turned_round), f"{label}: the build's sense read made again with the other Flip exactly "
              f"{list(turned_round)} on SolidWorks 2026: turned round {got}")
    elif TAG["major"] == 32:
        check(got == [], f"{label}: on SolidWorks 2024 every gear mate reads right as first made (probe "
              f"ring_mate_sense): turned round {got}")
    else:
        say(f"fact    {label}: the build's sense read made again with the other Flip: {got}")
    box = desk.record.gearbox
    check(box is not None and box.kind == store.GEARBOX_MOTION and box.assembly and desk.record.digest
          == desk.reading.digest, f"{label}: the record holds a turning gearbox built from this read")
    check(len(box.mates) == len(plan.motion.mates) and [m.name for m in box.mates] == [m.name for m in plan.motion.mates],
          f"{label}: the record's mates are the plan's: {[m.name for m in box.mates]}")
    drag = ui_text.drag_phrase(list(box.drag))
    # The phrase may open a sentence, capitalised there (W8's modes sentence: "… in any of them: … Drag InPin …").
    said = (drag, drag[:1].upper() + drag[1:])
    check(any(d in desk.note[0] for d in said), f"{label}: the build's sentence says how to turn it: {drag!r}")
    f = desk.say_footer(f"{label}, built")
    check(any(d in f.text for d in said), f"{label}: the footer says how to turn it: {drag!r}")
    say(f"tag     {ui_text.workbook_built_tag(desk.record, desk.reading.digest)!r}")
    paths = [box.layout, box.assembly] + sorted({c.part for c in box.components}) + [c.path for c in carriers_of(box)]
    check(all(os.path.isfile(p) for p in paths), f"{label}: {len(paths)} files on disk")
    check_fresh_build_marks(worker, paths, box.assembly, label)
    return plan, result


def frames_on_record(desk):
    box = desk.record.gearbox
    out = {c.gear: (tuple(c.rotation), tuple(c.at)) for c in box.components}
    out.update({wb_layout.carrier_id(c.shaft): (tuple(c.rotation), tuple(c.at)) for c in carriers_of(box)})
    return out


# -- the workbooks of b and c ------------------------------------------------------------------------------


def _f(v):
    return repr(round(v, 12))


ARC_R = 2 * (18 + 22) / 2           # stage 1: 18 / 22 teeth, module 2: 40 mm; stage 2: 17 / 23, also 40 mm


def spec_arc(folder, angle=30.0):
    x, y = ARC_R * math.cos(math.radians(angle)), ARC_R * math.sin(math.radians(angle))
    return GearboxSpec(
        box=Box(name="Arc_Move", output_folder=folder),
        shafts=(Shaft("S1", "frame", "0", "0", "0", "Z+", "input", speed="1000", torque="5"),
                Shaft("S2", "frame", _f(x), _f(y), "0", "Z+"),
                Shaft("S3", "frame", _f(x + 40), _f(y), "0", "Z+", "output")),
        gears=(Gear("G1", "S1", "5", "spur", "external", "18", "2", face_width="10", bore="6"),
               Gear("G2", "S2", "5", "spur", "external", "22", "2", face_width="10", bore="8"),
               Gear("G3", "S2", "20", "spur", "external", "17", "2", face_width="10", bore="8"),
               Gear("G4", "S3", "20", "spur", "external", "23", "2", face_width="10", bore="8")),
        meshes=(Mesh("G1", "G2"), Mesh("G3", "G4")))


def spec_risky(folder):
    """A helical pair across Z+ (S1) and Z- (S2); herringbones of 16 and 12 mm face on Z- (S2) and Z+ (S3); a
    helical pinion on Z+ (S3) in a helical ring whose shaft is Z- (S4). Small tooth counts, modest faces."""
    beta, beta_h = 20.0, 25.0
    a12 = 2 * (14 + 20) / (2 * math.cos(math.radians(beta)))
    a34 = 2 * (14 + 22) / (2 * math.cos(math.radians(beta_h)))
    a56 = 2 * (36 - 14) / (2 * math.cos(math.radians(beta)))
    s2, s3 = (a12, 0.0), (a12, -a34)
    s4 = (a12 + a56, -a34)
    return GearboxSpec(
        box=Box(name="Risky_Placements", output_folder=folder),
        shafts=(Shaft("S1", "frame", "0", "0", "0", "Z+", "input", speed="1000", torque="5"),
                Shaft("S2", "frame", _f(s2[0]), _f(s2[1]), "0", "Z-"),
                Shaft("S3", "frame", _f(s3[0]), _f(s3[1]), "0", "Z+"),
                Shaft("S4", "frame", _f(s4[0]), _f(s4[1]), "0", "Z-", "output")),
        gears=(Gear("G1", "S1", "5", "helical", "external", "14", "2", face_width="10", bore="6",
                    helix_angle=str(beta), hand="right"),
               Gear("G2", "S2", "-5", "helical", "external", "20", "2", face_width="10", bore="8",
                    helix_angle=str(beta), hand="left"),
               Gear("G3", "S2", "-24", "herringbone", "external", "14", "2", face_width="16", bore="8",
                    helix_angle=str(beta_h), hand="right"),
               Gear("G4", "S3", "24", "herringbone", "external", "22", "2", face_width="12", bore="8",
                    helix_angle=str(beta_h), hand="right"),
               Gear("G5", "S3", "45", "helical", "external", "14", "2", face_width="10", bore="8",
                    helix_angle=str(beta), hand="left"),
               Gear("G6", "S4", "-45", "helical", "internal", "36", "2", face_width="10",
                    helix_angle=str(beta), hand="left")),
        meshes=(Mesh("G1", "G2"), Mesh("G3", "G4"), Mesh("G5", "G6")))


def keep_fixture(book, name, neutral):
    """Save the workbook in Excel with a neutral Output folder and copy that file out as a fixture."""
    if not FIXTURES:
        return
    book.set("Box", "B4", neutral)
    book.save()
    os.makedirs(FIXTURES, exist_ok=True)
    shutil.copy2(book.path, os.path.join(FIXTURES, name))
    say(f"fixture {name} copied, as Excel saved it, with Output folder {neutral!r}")


# -- the W5 sections ------------------------------------------------------------------------------------------


def m7_unknown_mate(worker, desk, folder):
    """Review M7: an angle mate the record does not know, touching G4, unsuppressed -> Update refuses in its check
    phase naming it; suppressed -> Update goes through and lists it as left alone. Then deleted."""
    say("-- m1  M7: an angle mate Gear Generator did not make, on G4")
    box = desk.record.gearbox
    g4 = next(c.name for c in box.components if c.gear == "G4")

    def add(s):
        s.find_component("u4", g4)
        s.find_component("ulay", box.layout_component)
        name, _ = s.add_mate("user", "angle", "u4:plane2", "ulay:plane3", DRIVE_FROM)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        return name, s.mate_status(name)
    name, status = run(worker, in_assembly(box.assembly, add))
    say(f"        made {name!r} (SolidWorks' own name), AddMate5 status {status}")
    save_assembly(worker, desk, f"with {name}, so the marks after the refused press are its own")
    desk.plan_solidworks()
    desk.say_update()

    def mate_suppression(s):
        return [(m.name, m.suppressed) for m in s.mate_states()]
    frames_before = gear_frames(worker, desk)
    mates_before = run(worker, in_assembly(box.assembly, mate_suppression))
    flags_before = gearbox_flags(worker, desk)
    guard()
    _, result, _ = desk.update_solidworks()
    check(result is None and desk.error is not None and name in desk.note[0],
          f"M7: Update refuses, naming {name}: {desk.note[0]!r}")
    gap, at = frames_gap(gear_frames(worker, desk), frames_before)
    mates_after = run(worker, in_assembly(box.assembly, mate_suppression))
    flags_after = gearbox_flags(worker, desk)
    say(f"        M7: mates before {mates_before}; after {mates_after}; GetSaveFlag before {flags_before}, after "
        f"{flags_after}")
    check(gap <= FRAME_TOLERANCE and mates_after == mates_before and not marked(flags_before)
          and not marked(flags_after),
          f"M7: read from SolidWorks, the refusal changed nothing: every gear where it stood (largest {gap:.1e} at "
          f"{at or '-'}), every mate as it was (suppressed or not), nothing marked (before {marked(flags_before)}, "
          f"after {marked(flags_after)})")

    def suppress(s):
        s.find_mate("um", name)
        s.set_mate_suppressed("um", True)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    run(worker, in_assembly(box.assembly, suppress))
    say(f"        {name} suppressed in SolidWorks, as the sentence asks")
    save_assembly(worker, desk, f"with {name} suppressed, so the flags after the Update are its own")
    desk.plan_solidworks()
    frames_before = gear_frames(worker, desk)
    flags_before = gearbox_flags(worker, desk)
    guard()
    _, result, _ = desk.update_solidworks()
    if result is not None:
        check_quiet_update(worker, desk, result, "M7, suppressed", frames_before, flags_before)
    check(result is not None and result.ok and result.extra_mates == [name],
          f"M7: suppressed, Update goes through and lists it: extra mates {result and result.extra_mates}")
    check(result is not None and name in " ".join(result.log_lines()), f"M7: the log names {name} as left alone")
    run(worker, in_assembly(box.assembly, lambda s: (delete_mate(s, name), s.rebuild(kind=swcom.ASSEMBLY_TRAIN))))
    say(f"        {name} deleted")
    measure_mates(worker, desk, "m1 after M7")
    save_assembly(worker, desk, "after M7")
    desk.plan_solidworks()


def d10_suppressed_mate(worker, desk, folder):
    """D10: a recorded mate suppressed in SolidWorks -> Update turns it back on and says so."""
    say("-- m1  D10: G4 along S3 suppressed in SolidWorks")
    box = desk.record.gearbox
    mate = next(m.name for m in box.mates if m.kind == "along" and m.gears == ["G4"])

    def suppress(s):
        s.find_mate("dm", mate)
        s.set_mate_suppressed("dm", True)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    run(worker, in_assembly(box.assembly, suppress))
    save_assembly(worker, desk, f"with {mate} suppressed, so Update's own marks show")
    desk.plan_solidworks()
    desk.say_update()
    guard()
    _, result, _ = desk.update_solidworks()
    check(result is not None and result.ok and result.unsuppressed == [mate],
          f"D10: Update turned {mate} back on: unsuppressed {result and result.unsuppressed}")
    check(result is not None and mate in desk.note[0], f"D10: the sentence names {mate}: {desk.note[0]!r}")
    if result is not None:
        update_marks(worker, desk, result, "D10", folder)
    measure_frames(worker, desk, "m1 after D10")
    measure_mates(worker, desk, "m1 after D10")
    save_assembly(worker, desk, "after D10")
    desk.plan_solidworks()


def section_m1(worker, excel):
    say("== m1  the 12 : 1 fixture built to turn: §4.1, §4.2, M7, D10, the user's turn, At edits, the tooth change "
        "by the remake, Build again…")
    folder, path, book, desk = fixture_desk(worker, excel, "m1", FIXTURE_12)
    build_turning(worker, desk, "m1", 4)
    measure(worker, desk, "m1 built")
    drive_proof(worker, desk, "m1 built", control=("G3", "G4"))
    save_assembly(worker, desk, "after the drive, which left nothing behind")
    desk.plan_solidworks()
    m7_unknown_mate(worker, desk, folder)
    d10_suppressed_mate(worker, desk, folder)

    say("-- m1  the user's turn, simulated: 37°; then Update with nothing changed")
    user_turn(worker, desk, "m1", 37.0)
    save_assembly(worker, desk, "after the turn, as a person might")
    desk.plan_solidworks()
    update_nothing_turned(worker, desk, "m1 turned 37°", folder)

    say("-- m1  Excel: G4 At 27 -> 30")
    edit(desk, book, ("Gears", "C5", 30))
    u = desk.update
    check(u is not None and not u.needs_new_revision and list(u.axial) == ["G4"],
          f"classify: an Update moving G4 along S3: axial {u and list(u.axial)}, structural {u and list(u.structural)}")
    recorded = frames_on_record(desk)
    guard()
    _, result, _ = desk.update_solidworks()
    if result is not None:
        say_found(result, recorded, "G4 At")
        check(result.ok and result.axial == ["G4"], f"G4 At: \"G4 Face Z\" set: axial {result.axial}")
        restored = bool(result.restored)
        say(f"fact    G4 At: Update {'put the turned train back at its built turn' if restored else 'left the train turned'}"
            f": placed {result.placed}, restored {result.restored}, turned {result.turned}")
        check(restored == AXIAL_RESTORES and sorted(result.placed) == all_mated(desk)
              and sorted(g for r in result.restored for g in r) == all_mated(desk),
              f"G4 At: every gear of the turned train put back at its built turn, and restored names them (ruled on "
              f"2026-11-14): placed {result.placed}, restored {result.restored}")
        face = run(worker, lambda s: live_globals(s, desk.record.gearbox.assembly)).get("G4 Face Z")
        check(face is not None and abs(face - 20.0) < 1e-9, f"G4 At: the assembly's \"G4 Face Z\" reads {face} "
              "for 20 (At 30, face width 20)")
        update_marks(worker, desk, result, "G4 At", folder)
        check(result.clashes == [] and not result.interference_error, f"G4 At: no interference {result.clashes}")
        if restored:
            measure_frames(worker, desk, "m1 G4 At")
            measure_mates(worker, desk, "m1 G4 At")
            drive_proof(worker, desk, "m1 G4 At")
        else:
            measure_frames_turned(worker, desk, "m1 G4 At")
            say("        left turned: the drive waits for the train at its built turn (G3 At puts it back)")
            measure_mates(worker, desk, "m1 G4 At")
    save_assembly(worker, desk, "after G4 At")
    desk.plan_solidworks()

    say("-- m1  Excel: G3 At 27 -> 29 (a follower: an Update under suppressed locks)")
    edit(desk, book, ("Gears", "C4", 29))
    u = desk.update
    check(u is not None and not u.needs_new_revision and "G3" in u.replaced,
          f"classify: an Update re-placing G3 (LOCK_RETAKES_AN_OFFSET): structural {u and list(u.structural)}")
    guard()
    _, result, _ = desk.update_solidworks()
    if result is not None:
        check(result.ok and sorted(result.placed) == all_mated(desk), f"G3 At: every mated gear put (review M1): "
              f"placed {result.placed}")
        update_marks(worker, desk, result, "G3 At", folder)
        measure_frames(worker, desk, "m1 G3 At")
        measure_mates(worker, desk, "m1 G3 At")
        measure_clear(worker, desk, "m1 G3 At")
        drive_proof(worker, desk, "m1 G3 At")
    save_assembly(worker, desk, "after G3 At")
    desk.plan_solidworks()

    say("-- m1  Excel: the W4 demonstration edit: S2 X 63.75 -> 64.5, G2 Teeth 68 -> 69 (S3 X follows)")
    edit(desk, book, ("Shafts", "C3", 64.5), ("Gears", "F3", 69))
    u = desk.update
    check(u is not None and not u.needs_new_revision and [p.gear_ids for p in u.changed_parts] == [("G2",)]
          and u.moved_shafts == ("S2", "S3") and list(u.ratios) == ["G1 meshes G2"],
          "classify: an Update by the remake: G2's values, S2 and S3 moved, the gear mate G1 meshes G2 at 17 : 69")
    guard()
    before = stamps(folder, solidworks_only=True)
    _, result, _ = desk.update_solidworks()
    if result is not None:
        check(result.ok and result.ratios == ["G1 meshes G2"] and sorted(result.placed) == all_mated(desk),
              f"tooth change: the gear mate remade, every gear put: ratios {result.ratios}, placed {result.placed}")
        changed = sorted(os.path.basename(p) for p in result.changed)
        check(changed == ["Gear_m1.5_N68.SLDPRT", "Reducer_12to1.SLDASM", "Reducer_12to1_Layout.SLDPRT"],
              f"tooth change: changed {changed}")
        after = stamps(folder, solidworks_only=True)
        check([n for n in before if before[n] != after.get(n)] == [], "tooth change: Update saved nothing")
        entry = next(m for m in desk.record.gearbox.mates if m.name == "G1 meshes G2")
        check(list(entry.ratio) == [17, 69], f"tooth change: the record's G1 meshes G2 ratio {entry.ratio}")
        g2 = next(c for c in desk.record.gearbox.components if c.gear == "G2")
        teeth = run(worker, lambda s: live_globals(s, g2.part)).get("No. of Teeth")
        check(teeth is not None and abs(teeth - 69) < 1e-9, f"tooth change: G2's part holds \"No. of Teeth\" = {teeth}")
        update_marks(worker, desk, result, "tooth change", folder)
        measure_frames(worker, desk, "m1 tooth change")
        measure_mates(worker, desk, "m1 tooth change")
        measure_axes(worker, desk, "m1 tooth change")
        measure_clear(worker, desk, "m1 tooth change")
        drive_proof(worker, desk, "m1 at 17 : 69")
        reopen(worker, desk, "m1 tooth change")
    desk.plan_solidworks()

    say("-- m1  Excel: G1 face width 15 -> 17: its front face leaves the Front plane, so Build again…")
    edit(desk, book, ("Gears", "I2", 17))
    u = desk.update
    check(u is not None and u.needs_new_revision and any("G1's face width" in s and "Front plane" in s
                                                         for s in u.structural),
          f"classify: structural, the sentence naming the edit: {u and list(u.structural)}")
    desk.say_plan(full=False)
    p = desk.plan
    say(f"question {ui_text.build_again_question(desk.update, p, record=desk.record)}")
    check(p is not None and not p.refusal and p.revision == 2 and p.motion is not None,
          f"the plan: Reducer_12to1_r2, turning: revision {p and p.revision}")
    earlier, earlier_sidecars = stamps(folder), sidecar_texts(folder)
    guard()
    _, result = desk.build()
    later = check_earlier_unchanged(folder, earlier, "m1 build again", earlier_sidecars)
    say(f"        new files {sorted(n for n in later if n not in earlier)}")
    if result is not None:
        check(result.ok and result.kind == store.GEARBOX_MOTION and desk.record.gearbox.revision == 2,
              f"Reducer_12to1_r2 built turning: kind {result.kind!r}, revision {desk.record.gearbox.revision}")
        desk.say_footer("m1 _r2 built")
        measure(worker, desk, "m1 _r2")
        drive_proof(worker, desk, "m1 _r2", control=("G3", "G4"))
    book.close()


def measure_frames_turned(worker, desk, label):
    """A train left turned: every gear on its axis at its place (origins and axes against the read's frames), and
    in step (train_check against the read's frames)."""
    box = desk.record.gearbox
    names = [c.name for c in box.components]
    live = run(worker, lambda s: live_frames(s, box.assembly, names))
    want = wanted(desk)
    found = {c.gear: live[c.name] for c in box.components}
    for c in box.components:
        origin, _, residue = frame_error(found[c.gear], want[c.gear][:2], 0.0)
        check(origin <= FRAME_TOLERANCE and residue <= FRAME_TOLERANCE,
              f"{label}: {c.gear} on its axis at its place: origin off {origin:.1e} mm, axis off {residue:.1e}; turned "
              f"{turn_degrees(want[c.gear][0], found[c.gear][0])}°")
    links = desk.update.motion if desk.update is not None else None
    if links is not None:
        mated = [c.gear for c in box.components if c.gear not in box.fixed]
        tc = swbuild.train_check({g: found[g] for g in mated}, {g: want[g][:2] for g in mated}, links.meshes,
                                 links.locks, {g: want[g][2] for g in mated})
        say(f"        train_check: in step {tc.in_step}, turned {tc.turned}, residuals "
            f"{[(a, b, f'{r:.2e}') for a, b, r in tc.residuals]}")
        check(tc.in_step, f"{label}: the train in step")
    return found


def wrong_swing(worker, desk, label, folder):
    """W5-PLAN §4.3 m2: "the mates carry the gears, SolidWorks' wrong swing logged". Update makes the move and its
    puts in one job, so the swing between them cannot be read from outside it; the script makes the same move
    itself first — the layout's new globals set (``update.layout.variables``), the layout rebuilt, the assembly
    rebuilt top-only, as Update's step 2 does — reads where the mates carried each gear (origin against the read's
    new frame, turn against where it stood), logs it as facts, then closes the section's documents WITHOUT saving
    (``QuitDoc``), so the Update under test starts from the files: the turned train as saved."""
    box, u = desk.record.gearbox, desk.update
    variables = [(v.name, v.expression_for(base.DEGREES)) for v in u.layout.variables] if u and u.layout else []
    before = gear_frames(worker, desk)

    def work(s):
        s.begin_build()
        try:
            s.open_document(box.layout)
            for name, expression in variables:
                s.set_global_variable(name, expression)
            s.rebuild()
            s.open_document(box.assembly)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out = {}
            for index, c in enumerate(box.components):
                s.find_component(f"w{index}", c.name)
                out[c.gear] = s.component_frame(f"w{index}")
            return out
        finally:
            s.end_build()
    swung = run(worker, work)
    want = wanted(desk)
    say(f"        {label}: the layout's {[f'{n} = {e}' for n, e in variables]} set by the script, the assembly rebuilt")
    for gear, frame in swung.items():
        origin, _, residue = frame_error(frame, want[gear][:2], 0.0)
        say(f"fact    {label}, SolidWorks' swing: {gear} carried to its new place off by {origin:.2e} mm, axis off "
            f"{residue:.2e}; turned {turn_degrees(before[gear][0], frame[0])}° from where it stood, "
            f"{turn_degrees(want[gear][0], frame[0])}° from the read's new frame")
    left = run(worker, quit_in(folder))
    check(not left, f"{label}: the script's own move discarded (the section's documents closed without saving): "
          f"left {left}")


def section_m2(worker, excel):
    say("== m2  Arc_Move built to turn: §4.1, §4.2, the user's turn, then S2 moved along its arc")
    folder, path, book, desk = fixture_desk(worker, excel, "m2", FIXTURE_ARC)
    build_turning(worker, desk, "m2", 4)
    measure(worker, desk, "m2 built", again=False)
    drive_proof(worker, desk, "m2 built", control=("G1", "G2"))
    save_assembly(worker, desk, "after the drive")
    desk.plan_solidworks()
    say("-- m2  the user's turn, simulated: 25°; then Update with nothing changed")
    user_turn(worker, desk, "m2", 25.0)
    save_assembly(worker, desk, "after the turn")
    desk.plan_solidworks()
    update_nothing_turned(worker, desk, "m2 turned 25°", folder)
    say("-- m2  Excel: the angle 30 -> 40 (S2 and S3 move along the arc by formula)")
    edit(desk, book, ("Shafts", "L3", 40))
    u = desk.update
    check(u is not None and not u.needs_new_revision and not u.changed_parts and u.moved_shafts == ("S2", "S3"),
          "classify: no part values, S2 and S3 moved")
    wrong_swing(worker, desk, "m2 arc move", folder)
    recorded = frames_on_record(desk)
    guard()
    _, result, _ = desk.update_solidworks()
    if result is not None:
        say_found(result, recorded, "arc move")
        check(result.ok and result.layout is not None and sorted(result.layout.changed) == ["S2 X", "S2 Y", "S3 X",
                                                                                           "S3 Y"],
              f"arc move: the layout's S2 X, S2 Y, S3 X, S3 Y set: {result.layout and result.layout.changed}")
        check(sorted(result.placed) == all_mated(desk) and result.restored,
              f"arc move: the whole train put back at its built turn: placed {result.placed}, restored "
              f"{result.restored}")
        update_marks(worker, desk, result, "arc move", folder)
        measure_frames(worker, desk, "m2 moved")
        measure_axes(worker, desk, "m2 moved")
        measure_mates(worker, desk, "m2 moved")
        measure_clear(worker, desk, "m2 moved")
        drive_proof(worker, desk, "m2 moved")
        reopen(worker, desk, "m2 moved")
    book.close()


def section_m3(worker, excel):
    say("== m3  Risky_Placements built to turn: Z- shafts, compound shafts, a ring; §4.1, §4.2 with the control on "
        "the ring's mesh")
    folder, path, book, desk = fixture_desk(worker, excel, "m3", FIXTURE_RISKY)
    build_turning(worker, desk, "m3", 6, RING_TURNED_ROUND)
    measure(worker, desk, "m3 built")
    drive_proof(worker, desk, "m3 built", control=("G5", "G6"))
    save_assembly(worker, desk, "after the drive")
    desk.plan_solidworks()
    say("-- m3  the user's turn, simulated: 20°; then Update with nothing changed")
    user_turn(worker, desk, "m3", 20.0)
    save_assembly(worker, desk, "after the turn")
    desk.plan_solidworks()
    update_nothing_turned(worker, desk, "m3 turned 20°", folder)
    book.close()


def section_m7(worker, excel):
    say("== m7  the ring train edited: Risky_Placements built to turn, G5 At 45 -> 47 (a follower on S3, beside the "
        "ring's pinion seat) -> an Update that puts the whole train; frames, mates, interference, the drive through the "
        "ring, reopen")
    folder, path, book, desk = fixture_desk(worker, excel, "m7", FIXTURE_RISKY)
    build_turning(worker, desk, "m7", 6, RING_TURNED_ROUND)
    measure(worker, desk, "m7 built", controls=False, again=False)
    edit(desk, book, ("Gears", "C6", 47))
    u = desk.update
    check(u is not None and not u.needs_new_revision and "G5" in u.replaced,
          f"classify: an Update re-placing G5 (LOCK_RETAKES_AN_OFFSET): structural {u and list(u.structural)}")
    guard()
    _, result, _ = desk.update_solidworks()
    if result is not None:
        check(result.ok and sorted(result.placed) == all_mated(desk) and result.ratios == [],
              f"m7: every mated gear put, no gear mate remade: placed {result.placed}, ratios {result.ratios}")
        update_marks(worker, desk, result, "m7 G5 At", folder)
        measure_frames(worker, desk, "m7 G5 At")
        measure_mates(worker, desk, "m7 G5 At")
        measure_clear(worker, desk, "m7 G5 At")
        negative_controls(worker, desk, "m7 G5 At")
        drive_proof(worker, desk, "m7 G5 At, through the ring", control=("G5", "G6"))
        reopen(worker, desk, "m7 G5 At")
    book.close()


def ring_mate_reading(worker, desk, name):
    """The app's own read-back of a ring's gear mate (``Session.gear_mate_sense``, W6's form: the two gears' axes as
    recorded and the mesh's same sense; reading only): whether it reads right, whether its two entity directions
    point the same way, and its Reverse as the rule gives it."""
    box = desk.record.gearbox
    rotation = {c.gear: c.rotation for c in box.components}
    axes = tuple((rotation[g][2], rotation[g][5], rotation[g][8]) for g in name.split(" meshes "))
    same_sense = sum(p * q for p, q in zip(*axes)) > 0      # inside a ring k = +(a_a·a_b)·za/zb

    def work(s):
        s.find_mate("ring", name)
        return s.gear_mate_sense("ring", same_sense, axes)
    right, taus = run(worker, in_assembly(box.assembly, work))
    parallel = taus[0] * taus[1] * (1 if same_sense else -1) > 0   # the entity directions, d = τ·g, point alike
    reverse = parallel if right else not parallel          # internal: right == (Reverse == parallel)
    say(f"fact    {name} read back: right {right}; its axes {'parallel' if parallel else 'opposed'}; Reverse {reverse}")
    return right, parallel, reverse


def section_m8(worker, excel):
    say("== m8  the ring's gear mate made again after a move: Risky_Placements built to turn; G5 At 45 -> 47 by Update; "
        "then the ring mesh's teeth 14/36 -> 15/37 (the same centre distance) by Update: the app remakes G5 meshes G6")
    folder, path, book, desk = fixture_desk(worker, excel, "m8", FIXTURE_RISKY)
    build_turning(worker, desk, "m8", 6, RING_TURNED_ROUND)
    ring_mate_reading(worker, desk, "G5 meshes G6")
    say("-- m8  Excel: G5 At 45 -> 47 (the ring's pinion moves 2 mm along S3)")
    edit(desk, book, ("Gears", "C6", 47))
    guard()
    _, result, _ = desk.update_solidworks()
    check(result is not None and result.ok and result.ratios == [], f"m8: G5 moved by Update, no gear mate remade: "
          f"{result and result.ratios}")
    save_assembly(worker, desk, "after G5 At")
    desk.plan_solidworks()

    say("-- m8  Excel: G5 Teeth 14 -> 15, G6 Teeth 36 -> 37 (centre distance kept)")
    edit(desk, book, ("Gears", "F6", 15), ("Gears", "F7", 37))
    u = desk.update
    if u is None or u.needs_new_revision or u.refusal:
        say(f"fact    m8: the app does not carry the ring tooth change as an Update: structural "
            f"{u and list(u.structural)}; refusal {u and u.refusal!r}; summary {u and ui_text.update_summary(u)!r}")
        check(False, "m8: the ring tooth change is an Update the app remakes the ring's gear mate in")
        book.close()
        return
    check(list(u.ratios) == ["G5 meshes G6"], f"classify: an Update remaking G5 meshes G6 at 15 : 37: ratios "
          f"{list(u.ratios)}")
    guard()
    _, result, _ = desk.update_solidworks()
    if result is None:
        check(False, f"m8: the Update refused: {desk.note[0]!r}")
        book.close()
        return
    say(f"fact    m8: the remake: ratios {result.ratios}, ratios_read {result.ratios_read}, turned round "
        f"{getattr(result, 'turned_round', None)}, sense found wrong {getattr(result, 'sense_found_wrong', None)}")
    check(result.ok and result.ratios == ["G5 meshes G6"], f"m8: the app remade G5 meshes G6 at 15 : 37: ratios "
          f"{result.ratios}; {desk.note[0]!r}")
    right, _, _ = ring_mate_reading(worker, desk, "G5 meshes G6")
    check(right, "m8: the remade ring gear mate reads right by the app's own read-back")
    update_marks(worker, desk, result, "m8 ring remake", folder)
    measure_frames(worker, desk, "m8 remade")
    measure_mates(worker, desk, "m8 remade")
    measure_clear(worker, desk, "m8 remade")
    negative_controls(worker, desk, "m8 remade")
    # The judge: G6 must turn the right way at 15 : 37 (the drive's kinematics come from the read, now 15/37).
    drive_proof(worker, desk, "m8 at 15 : 37, through the remade ring mate", control=("G5", "G6"))
    save_assembly(worker, desk, "after the remake and the drive")
    desk.plan_solidworks()
    say("-- m8  Update pressed again with nothing changed")
    frames_before, flags_before = gear_frames(worker, desk), gearbox_flags(worker, desk)
    guard()
    _, result, _ = desk.update_solidworks()
    if result is not None:
        check(result.ok and result.ratios == [] and not list(getattr(result, "sense_found_wrong", []) or []),
              f"m8: nothing to do: ratios {result.ratios}, sense found wrong {getattr(result, 'sense_found_wrong', None)}")
        check_quiet_update(worker, desk, result, "m8 quiet Update", frames_before, flags_before)
    reopen(worker, desk, "m8 remade")
    ring_mate_reading(worker, desk, "G5 meshes G6")
    drive_proof(worker, desk, "m8 reopened, at 15 : 37")
    book.close()


def spec_ring_shift(name, folder, shift, centre):
    """A spur pinion (14 teeth, module 2, profile shift ``shift``) on S1 (Z+, input) inside an unshifted spur ring
    (36 teeth) on S2 (Z-, output, as Risky_Placements' ring), the shafts ``centre`` mm apart; the faces overlap."""
    return GearboxSpec(
        box=Box(name=name, output_folder=folder),
        shafts=(Shaft("S1", "frame", "0", "0", "0", "Z+", "input", speed="1000", torque="5"),
                Shaft("S2", "frame", _f(centre), "0", "0", "Z-", "output")),
        gears=(Gear("G1", "S1", "5", "spur", "external", "14", "2", face_width="10", bore="6",
                    profile_shift=_f(shift)),
               Gear("G2", "S2", "-5", "spur", "internal", "36", "2", face_width="10")),
        meshes=(Mesh("G1", "G2"),))


def ring_shift(worker, excel, section, name, shift, working):
    """A shifted pinion in a ring: at its working centre distance (checks.internal_working_centre) built and
    judged; at the plain 22 mm the Checks panel must refuse it before any build."""
    from gear_generator.workbook import checks as wb_checks
    centre = wb_checks.internal_working_centre(2.0, 14, 36, 20.0, pinion_shift=shift) if working else 22.0
    say(f"== {section}  a 14-tooth spur pinion shifted {shift:+g} inside an unshifted 36-tooth ring, the shafts "
        f"{centre:.9f} mm apart ({'its working centre distance, from checks.internal_working_centre' if working else 'the plain 22 mm'})")
    folder = fresh_folder(section)
    path = os.path.join(folder, f"{name}.xlsx")
    xlsx.write_new(path, wb_model.to_sheets(spec_ring_shift(name, folder + "\\", shift, centre)))
    book = Workbook(excel, path, section)
    book.set("Box", "B4", folder + "\\")
    book.save()
    desk = Desk(path, worker)
    desk.read()
    errors = [d for d in desk.a.diagnostics if d.level == "error"]
    fixes = {where: [(f.title, f.detail, [(e.sheet, e.item, e.key, e.value) for e in f.edits]) for f in found]
             for where, found in desk.a.report.fixes.items()}
    say(f"        centres on record {dict(desk.a.report.centres)}; errors {[d.message for d in errors]}; fixes {fixes}")
    if not working:
        check(bool(desk.a.lay_out_refusal()) and any("apart" in d.message for d in errors),
              f"{section}: the Checks panel refuses the pair before any build: {[d.message for d in errors]}")
        say(f"fact    {section}: the fixes offered: {fixes}")
        desk.say_footer(f"{section}, refused")
        book.close()
        return
    check(desk.a.lay_out_refusal() == "" and not errors, f"{section}: the workbook checks clean (no error): gate "
          f"{desk.a.lay_out_refusal()!r}")
    _, result = build_turning(worker, desk, section, 2, None)
    say(f"fact    {section}: the app's interference result as built: clashes "
        f"{[(c.gears, round(c.volume, 6)) for c in result.clashes]}, error {result.interference_error!r}")
    measure(worker, desk, f"{section} built", controls=True, again=False)
    pitch = 360.0 / 14
    drive_proof(worker, desk, f"{section}, through the mesh", control=("G1", "G2"),
                phases=(pitch / 4, pitch / 2, 3 * pitch / 4))
    book.close()


# The ring-shift checks, run as r1–r3 on 2026-11-14 (ring-shift-2026-20261114-185630.log), renamed rs1–rs3 when W6
# took r1–r6 for its own sections.
def section_rs1(worker, excel):
    ring_shift(worker, excel, "rs1", "Ring_Shift_Plus", 0.3, True)


def section_rs2(worker, excel):
    ring_shift(worker, excel, "rs2", "Ring_Shift_Minus", -0.3, True)


def section_rs3(worker, excel):
    ring_shift(worker, excel, "rs3", "Ring_Shift_Plain", 0.3, False)


def injected(plan, offset):
    """The m4 plan: the turning assembly's ops with G3 — the follower locked to G2 — also mated on S2 Axis and along
    S2 (``offset`` mm off where it stands), right after its lock (W5-PLAN §4.3 m4: over-defined, as probe
    compound_lock found)."""
    handle_of = {g: h for h, g in plan.handles.items()}
    h3 = handle_of["G3"]
    z = plan.frames["G3"].at[2] + offset
    ops, done = [], False
    for op in plan.assembly.ops:
        ops.append(op)
        if not done and isinstance(op, base.Mate) and op.kind == "lock" and op.b == h3:
            ops.append(base.Mate("inject1", "coincident", f"{h3}:Gear Axis", f"{wb_layout.LAYOUT_HANDLE}:S2 Axis",
                                 name="G3 on S2 Axis"))
            ops.append(base.Mate("inject2", "point distance", f"{h3}:origin", f"{wb_layout.LAYOUT_HANDLE}:plane1", z,
                                 name="G3 along S2"))
            done = True
    if not done:
        raise AssertionError("m4: the plan has no lock on G3 to inject beside")
    return dataclasses.replace(plan, assembly=dataclasses.replace(plan.assembly, ops=tuple(ops)))


FOLDER_CONTAINING = 2       # swFeatureTreeFolderType_e.swFeatureTreeFolder_Containing, as probe mate_folders read it


def mate_folder(session, names, folder_name):
    """``findings.MATE_FOLDER_ROUTE``, as probe mate_folders made one: the mates selected (Select2, appending after
    the first), ``IFeatureManager.InsertFeatureTreeFolder2(swFeatureTreeFolder_Containing)``, the folder renamed, a
    top-only rebuild. Returns the mate group's walk as (name, GetTypeName2)."""
    doc = session._doc()  # noqa: SLF001
    call(doc, "ClearSelection2", True)
    for index, name in enumerate(names):
        call(session._mate_feature(name), "Select2", index > 0, 0)  # noqa: SLF001
    folder = call(call(doc, "FeatureManager"), "InsertFeatureTreeFolder2", FOLDER_CONTAINING)
    call(doc, "ClearSelection2", True)
    if folder is None:
        raise swcom.SolidWorksError("InsertFeatureTreeFolder2 made no folder")
    folder.Name = folder_name
    session.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    return mate_walk(session)


def mate_walk(session):
    """The mate group as SolidWorks lists it: (name, GetTypeName2) of every entry, folders included."""
    return [(str(call(f, "Name")), swcom._type_name(f)) for f in session._mate_group()]  # noqa: SLF001


FOLDER_NAME = "Gear mates"


def in_folder(walk, names, folder_name=FOLDER_NAME):
    """Which of ``names`` the walk lists between the folder's own entry and its end tag (probe mate_folders: a
    folder reads as its entry, its mates as ordinary following entries, then "<FolderN>___EndTag___", both of type
    findings.MATE_FOLDER_TYPE_NAME). Returns (inside, outside); everything is outside when there is no folder."""
    kinds = findings.MATE_FOLDER_TYPE_NAME
    starts = [i for i, (n, t) in enumerate(walk) if t == kinds and n == folder_name]
    ends = [i for i, (n, t) in enumerate(walk) if t == kinds and n.endswith("___EndTag___")]
    if not starts or not [e for e in ends if e > starts[0]]:
        return [], list(names)
    first, last = starts[0], min(e for e in ends if e > starts[0])
    position = {n: i for i, (n, _) in enumerate(walk)}
    inside = [n for n in names if n in position and first < position[n] < last]
    return inside, [n for n in names if n not in inside]


def check_folder(walk, names, label, outside=()):
    inside, out = in_folder(walk, names)
    want_in = [n for n in names if n not in outside]
    check(inside == want_in and sorted(out) == sorted(outside),
          f"{label}: inside the folder {FOLDER_NAME!r} (between its entry and its end tag): {inside}; outside it: "
          f"{out} (wanted outside: {list(outside)})")


def folder_suppressed(session, folder_name, suppress=None):
    """The mate folder ``folder_name`` in the build document's mate group: suppressed or turned on by the call that
    suppresses a mate (``IFeature.SetSuppression2(findings.FEATURE_SUPPRESS or FEATURE_UNSUPPRESS,
    THIS_CONFIGURATION, None)``, as probe round P0d suppressed a folder) when ``suppress`` is given; returns whether
    it reads suppressed, and each entry's (name, suppressed)."""
    folder = next((f for f in session._mate_group() if str(call(f, "Name")) == folder_name  # noqa: SLF001
                   and swcom._type_name(f) == findings.MATE_FOLDER_TYPE_NAME), None)  # noqa: SLF001
    if folder is None:
        raise swcom.SolidWorksError(f"No mate folder called {folder_name!r}.")
    if suppress is not None:
        action = findings.FEATURE_SUPPRESS if suppress else findings.FEATURE_UNSUPPRESS
        call(folder, "SetSuppression2", action, findings.THIS_CONFIGURATION, None)
        session.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    return (session._is_suppressed(folder),  # noqa: SLF001
            [(str(call(f, "Name")), session._is_suppressed(f)) for f in session._mate_group()])  # noqa: SLF001


def section_m6(worker, excel):
    say("== m6  the 12 : 1's gear mates in a mate folder, saved and reopened; an Update that puts the whole train; "
        "then a tooth change whose remade gear mate lands outside the folder")
    folder, path, book, desk = fixture_desk(worker, excel, "m6", FIXTURE_12)
    build_turning(worker, desk, "m6", 4)
    measure(worker, desk, "m6 built", controls=False, again=False)
    box = desk.record.gearbox
    gear_mates = [m.name for m in box.mates if m.kind == "mesh"]
    walk = run(worker, in_assembly(box.assembly, lambda s: mate_folder(s, gear_mates, FOLDER_NAME)))
    say(f"        the mate group with the folder: {walk}")
    check_folder(walk, gear_mates, "m6, the folder made")
    measure_mates(worker, desk, "m6 with the folder")
    reopen(worker, desk, "m6 with the folder")
    walk = run(worker, in_assembly(box.assembly, mate_walk))
    say(f"        the mate group reopened: {walk}")
    check_folder(walk, gear_mates, "m6, reopened")

    say("-- m6  Excel: G3 At 27 -> 29, an Update that puts the whole train with the gear mates in the folder")
    edit(desk, book, ("Gears", "C4", 29))
    guard()
    _, result, _ = desk.update_solidworks()
    check(result is not None and result.ok and sorted(result.placed) == all_mated(desk),
          f"m6: the Update passed with the mates in a folder and put every gear: {desk.note[0]!r}")
    say(f"        the app's own report of the mates: {[(m.name, m.code, m.suppressed) for m in result.mates] if result else None}")
    walk = run(worker, in_assembly(box.assembly, mate_walk))
    say(f"        the mate group after the Update: {walk}")
    check_folder(walk, gear_mates, "m6, after the Update")
    if result is not None:
        update_marks(worker, desk, result, "m6 G3 At", folder)
        measure_frames(worker, desk, "m6 G3 At")
        # The check that every recorded mate is still there and sound is SolidWorks' side, read by measure_mates.
        measure_mates(worker, desk, "m6 G3 At (every recorded mate found in SolidWorks)")
        measure_clear(worker, desk, "m6 G3 At")
    save_assembly(worker, desk, "after G3 At")
    desk.plan_solidworks()

    say("-- m6  the folder holding the gear mates suppressed in SolidWorks (which suppresses both), then Update")
    state = run(worker, in_assembly(box.assembly, lambda s: folder_suppressed(s, FOLDER_NAME, True)))
    say(f"        folder suppressed: {state[0]}; entries {state[1]}")
    check(state[0] and all(sup for n, sup in state[1] if n in gear_mates),
          f"m6: the folder reads suppressed, and so does every gear mate in it: {state}")
    save_assembly(worker, desk, "with the folder suppressed, so Update's own marks show")
    desk.plan_solidworks()
    desk.say_update()
    guard()
    _, result, _ = desk.update_solidworks()
    if result is None:
        check(False, f"m6, folder suppressed: Update refused: {desk.note[0]!r}")
    else:
        check(result.ok and sorted(result.unsuppressed) == sorted(gear_mates) and result.ratios == []
              and not list(getattr(result, "sense_found_wrong", []) or []),
              f"m6, folder suppressed: Update turned every gear mate back on, remade none, found none turning the "
              f"wrong way: unsuppressed {result.unsuppressed}, ratios {result.ratios}, sense found wrong "
              f"{getattr(result, 'sense_found_wrong', None)}, turned round {getattr(result, 'turned_round', None)}")
        state = run(worker, in_assembly(box.assembly, lambda s: folder_suppressed(s, FOLDER_NAME)))
        say(f"fact    m6, after the Update: the folder reads suppressed {state[0]}; entries {state[1]}")
        update_marks(worker, desk, result, "m6 folder suppressed", folder)
        measure_frames(worker, desk, "m6 folder back on")
        measure_mates(worker, desk, "m6 folder back on (every gear mate on, read in SolidWorks)")
        walk = run(worker, in_assembly(box.assembly, mate_walk))
        check_folder(walk, gear_mates, "m6, the gear mates turned back on")
        drive_proof(worker, desk, "m6 folder back on, the gear mates' sense")
    save_assembly(worker, desk, "after the folder step")
    desk.plan_solidworks()

    say("-- m6  Excel: S2 X 64.5, G2 Teeth 69: the remade G1 meshes G2 lands at the end of the mate group, outside "
        "the folder (W5-DECISIONS on P0c), and is left there")
    edit(desk, book, ("Shafts", "C3", 64.5), ("Gears", "F3", 69))
    guard()
    _, result, _ = desk.update_solidworks()
    check(result is not None and result.ok and result.ratios == ["G1 meshes G2"],
          f"m6: the gear mate in the folder remade at 17 : 69: ratios {result and result.ratios}")
    walk = run(worker, in_assembly(box.assembly, mate_walk))
    say(f"        the mate group after the remake: {walk}")
    check_folder(walk, gear_mates, "m6, after the remake", outside=("G1 meshes G2",))
    check(bool(walk) and walk[-1][0] == "G1 meshes G2", f"m6: the remade gear mate is the last entry of the mate "
          f"group: {walk[-1] if walk else None}")
    if result is not None:
        measure_frames(worker, desk, "m6 remade")
        measure_mates(worker, desk, "m6 remade (every recorded mate found in SolidWorks)")
        measure_clear(worker, desk, "m6 remade")
        drive_proof(worker, desk, "m6 at 17 : 69, one gear mate in the folder and one outside")
        reopen(worker, desk, "m6 remade")
        walk = run(worker, in_assembly(box.assembly, mate_walk))
        say(f"        the mate group reopened after the remake: {walk}")
        check_folder(walk, gear_mates, "m6, reopened after the remake", outside=("G1 meshes G2",))
    book.close()


def p0c_findings():
    """What probe round P0c set, by name (read when it is committed; logged whatever it is)."""
    keys = ("SECOND_ASSEMBLY", "COMMAND_IN_PROGRESS", "LIGHTWEIGHT", "MATE_FOLDER", "FOLDER", "IDLER",
            "UNSUPPRESS_ON", "SUPPRESSED_MATE", "RENAME_AT_ONCE", "TWICE_MESHED")
    return {name: getattr(findings, name) for name in dir(findings) if name.isupper() and any(k in name for k in keys)}


def refused_state(session, title):
    """The refused, never-saved assembly ``title``: its components' constrained statuses and its mates' states,
    read in place (it has no file to open), changing nothing."""
    app = session._app  # noqa: SLF001
    doc = next((d for d in documents(app) if str(call(d, "GetTitle")) == title), None)
    if doc is None:
        return None
    comps = call(doc, "GetComponents", True) or ()
    status = {str(call(c, "Name2")): swcom._read(c, "GetConstrainedStatus") for c in comps}  # noqa: SLF001
    session.begin_build()
    try:
        session._build_doc = doc  # noqa: SLF001 - read the refused document's mate group in place
        others = []
        states = session.mate_states(others=others)
    finally:
        session.end_build()
    return {"path": str(call(doc, "GetPathName") or ""), "modified": bool(call(doc, "GetSaveFlag")),
            "constrained": status, "mates": [(s.name, s.code, s.warning, s.suppressed) for s in states],
            "others": others}


def m4_attempt(worker, excel, section, offset):
    """One forced build: the 12 : 1 in its own folder, G3 given the extra mates ``offset`` mm off where it stands.
    Logs everything SolidWorks reported; returns (folder, book, desk, result, refused)."""
    folder, path, book, desk = fixture_desk(worker, excel, section, FIXTURE_12)
    desk.say_plan(full=False)
    plan = injected(desk.plan, offset)
    say(f"        injected ({offset:g} mm off): "
        f"{[base.describe(op) for op in plan.assembly.ops if getattr(op, 'id', '').startswith('inject')]}")
    guard()
    _, result = desk.build(plan)
    if result is None:
        raise AssertionError(f"{section}: the build raised: {desk.note[0]}")
    asm = result.assembly
    names = [op.name for op in plan.assembly.ops if isinstance(op, base.Mate)]
    statuses = run(worker, lambda s: {n: s.mate_status(n) for n in names})
    say(f"        AddMate5 statuses {statuses}")
    say(f"        mate states {[(s.name, s.code, s.warning, s.suppressed) for s in (asm.mates if asm else [])]}")
    say(f"        mate problems {asm.mate_problems if asm else None}; failures {asm.failures if asm else None}")
    say(f"        left open as {asm.document if asm else None!r}; saved {asm.saved if asm else None!r}")
    refused = bool(asm is not None and asm.mate_problems and not asm.saved)
    if refused and asm.document:
        REFUSED.append(asm.document)
        state = run(worker, lambda s: refused_state(s, asm.document))
        say(f"        the refused document as it stands (constrained statuses, mates): {state}")
        check(state is not None and not state["path"], f"{section}: {asm.document} is open, never saved")
    elif not refused and desk.record is not None and desk.record.gearbox is not None and desk.record.gearbox.assembly:
        box = desk.record.gearbox
        states, others, status = run(worker, lambda s: live_mates(s, box.assembly,
                                                                  [(c.gear, c.name) for c in box.components]))
        say(f"        the assembly SolidWorks saved: mates {[(x.name, x.code, x.warning, x.suppressed) for x in states]}; "
            f"others {others}; constrained {status}")
    return folder, book, desk, result, refused


def section_m4(worker, excel):
    say("== m4  a refused mate, forced: G3 also on S2 Axis and along S2 -> the build stops")
    say(f"findings P0c {p0c_findings()}")
    # Ruled on 2026-11-14: the consistent extra mates first; if SolidWorks accepts them (nothing the app's mate check
    # flags), that is a finding, and the build is forced again with the along mate 1 mm off.
    offsets = [M4_OFFSET] + ([1.0] if M4_OFFSET == 0.0 else [])
    for index, offset in enumerate(offsets):
        section = "m4" if index == 0 else f"m4-offset{offset:g}"
        say(f"-- {section}  the extra mates {offset:g} mm off where G3 stands")
        folder, book, desk, result, refused = m4_attempt(worker, excel, section, offset)
        if refused:
            say(f"fact    m4: the refusal was made by the extra mates {offset:g} mm off "
                f"({'consistent with where G3 stands' if offset == 0.0 else 'conflicting with the lock'})")
            break
        say(f"fact    m4: FINDING: SolidWorks accepted the extra mates {offset:g} mm off — no AddMate5 status, error "
            "code, warning or constrained status the app's mate check flags — and the assembly was saved: kind "
            f"{result.kind!r}")
        left = run(worker, close_ours)
        say(f"        {section} closed: left {left}")
        book.close()
    else:
        check(False, f"m4: no case made the refusal (offsets {offsets})")
        return
    asm = result.assembly
    check(asm.mate_problems and not asm.saved and asm.document,
          f"{section}: the build stopped at the mate check, the assembly not saved, left open as {asm.document!r}")
    check(not os.path.exists(os.path.join(folder, "Reducer_12to1.SLDASM")), f"{section}: no assembly file")
    check(result.kind == "", f"{section}: nothing saved in its place: kind {result.kind!r}")
    rec = desk.record
    check(rec is not None and len(rec.parts) == 4 and rec.gearbox.layout and not rec.gearbox.assembly
          and all(os.path.isfile(e.path) for e in rec.parts) and os.path.isfile(rec.gearbox.layout),
          "m4: the parts and the layout part saved and on record, no assembly on record")
    check(rec is not None and rec.gearbox.mate_problems == list(asm.mate_problems)
          and rec.gearbox.mate_problems_digest == desk.reading.digest,
          f"m4: the record's mate problems and their digest: {rec and rec.gearbox.mate_problems}")
    f = desk.say_footer("refused")
    check(not f.build_enabled and "Build is available again once the workbook changes" in f.text,
          "m4: the footer never offers the same build of the unchanged workbook")
    check(any(p in desk.note[0] for p in asm.mate_problems), "m4: the sentence names the mate SolidWorks refused or "
          "flagged")

    say("-- m4  a note cell changed in Excel (the plan unchanged, without the injection): Build again")
    edit(desk, book, ("Meshes", "D3", "stage 2, refused once"))
    f = desk.say_footer("the workbook changed")
    desk.say_plan(full=False)
    p = desk.plan
    check(f.build_enabled and p is not None and p.revision == 0 and not p.build and len(p.reuse) == 4
          and isinstance(p.layout, wb_gearbox.LayoutReuse),
          "m4: Build on again; the same revision, the parts and the layout reused, only the assembly to make")
    beside = next((v for k, v in p0c_findings().items() if "SECOND_ASSEMBLY" in k and isinstance(v, bool)), None)
    if beside is not True and asm is not None and asm.document:
        say(f"        P0c's finding on a second assembly beside an unsaved one is {beside!r}: the refused one is "
            "closed first")
        left = run(worker, close_ours)
        check(not left, f"m4: closed: left {left}")
    else:
        say(f"        the refused {asm.document if asm else ''} stays open beside the new build (P0c: {beside!r})")
    guard()
    _, result = desk.build()
    if result is not None:
        check(result.ok and result.kind == store.GEARBOX_MOTION and desk.record.gearbox.revision == 0
              and os.path.isfile(os.path.join(folder, "Reducer_12to1.SLDASM")),
              f"m4: the assembly made at the same revision, turning: kind {result.kind!r}")
        check(desk.record.gearbox.mate_problems == [] and desk.record.gearbox.mate_problems_digest == "",
              "m4: the record's mate problems emptied once an assembly saved")
        say(f"open    {run(worker, open_titles)}")
        measure(worker, desk, "m4 built after the refusal", controls=False, again=False)
        PERSON.append(("m4", desk.record.gearbox.assembly))
    say("-- m4  the refused document closed, as W4's close_ours closes on 2024 (modified documents saved first)")
    left = run(worker, close_ours)
    check(not left, f"m4: closed, the refused one by its title: left {left}")
    book.close()


def section_m5(worker, excel):
    say("== m5  an Update lost and pressed again: the demonstration edit, every document closed without saving, "
        "Update pressed on the same workbook")
    folder, path, book, desk = fixture_desk(worker, excel, "m5", FIXTURE_12)
    build_turning(worker, desk, "m5", 4)
    measure(worker, desk, "m5 built", controls=False, again=False)
    edit(desk, book, ("Shafts", "C3", 64.5), ("Gears", "F3", 69))
    guard()
    _, result, _ = desk.update_solidworks()
    check(result is not None and result.ok and result.ratios == ["G1 meshes G2"], "m5: the first Update remade the "
          "gear mate at 17 : 69")
    left = run(worker, quit_in(folder))
    check(not left, f"m5: every document of the section closed in SolidWorks without saving: left {left}")
    desk.plan_solidworks()
    desk.say_update()
    desk.say_footer("documents closed unsaved")
    guard()
    _, result, _ = desk.update_solidworks()
    if result is not None:
        check(result.ok and LOST_SENTENCE in desk.note[0], f"m5: the sentence says the lost Update was made again: "
              f"{desk.note[0]!r}")
        check(result.ratios == ["G1 meshes G2"] and result.ratios_found == ["G1 meshes G2"],
              f"m5: the gear mate, found live at 17 : 68 (the file's), remade once at 17 : 69: ratios {result.ratios}, "
              f"ratios_found {result.ratios_found}")
        check([tuple(r) for r in result.ratios_read] == [("G1 meshes G2", 17, 68, 17, 69)],
              f"m5: Update read the gear mate at 17 : 68 and wanted 17 : 69: ratios_read {result.ratios_read}")
        check(REMADE_SENTENCE in desk.note[0], f"m5: the sentence names both ratios: {REMADE_SENTENCE!r}")
        measure_frames(worker, desk, "m5 pressed again")
        measure_mates(worker, desk, "m5 pressed again")
        drive_proof(worker, desk, "m5 pressed again, at the record's 17 : 69")
    book.close()


# -- W4's sections, on turning builds -------------------------------------------------------------------------


def section_a(worker, excel):
    say("== a   the 12 : 1 fixture: build, measure, Update SolidWorks (the tooth change by the remake), build again "
        "as _r2")
    folder, path, book, desk = fixture_desk(worker, excel, "a", FIXTURE_12)
    desk.say_footer("read")
    desk.say_plan()
    check(desk.plan is not None and desk.plan.revision == 0 and len(desk.plan.build) == 4 and not desk.plan.reuse,
          "the plan: revision 0, four parts to make, nothing to reuse")
    say(f"open    before: {run(worker, open_titles)}")
    guard()
    plan, result = desk.build()
    made = [os.path.join(folder, n) for n in ("Gear_m1.5_N17.SLDPRT", "Gear_m1.5_N68.SLDPRT", "Gear_m2_N17.SLDPRT",
                                              "OutputGear.SLDPRT", "Reducer_12to1_Layout.SLDPRT",
                                              "Reducer_12to1.SLDASM")]
    check(result.ok and all(os.path.isfile(p) for p in made), "4 parts, the layout part and the assembly saved")
    check(result.kind == store.GEARBOX_MOTION, f"built turning: kind {result.kind!r}")
    check(result.clashes == [] and not result.interference_error, f"no interference: {result.clashes}")
    check_fresh_build_marks(worker, made, made[-1], "a")
    check(desk.record is not None and desk.record.digest == desk.reading.digest and desk.record.gearbox.assembly,
          "the record holds the gearbox, built from this read")
    desk.say_footer("after the build")
    say(f"tag     {ui_text.workbook_built_tag(desk.record, desk.reading.digest)!r}")
    guard()
    measure(worker, desk, "a built")
    first = frames_on_record(desk)

    say("-- a   the demonstration edit in Excel: S2 X 63.75 -> 64.5, G2 Teeth 68 -> 69")
    guard()
    before_update = stamps(folder, solidworks_only=True)
    book.set("Shafts", "C3", 64.5)
    book.set("Gears", "F3", 69)
    book.save()
    say(f"excel   Shafts!C4 now reads {book.get('Shafts', 'C4')!r} by its formula")
    reading = desk.poll()
    for line in ("Shafts!C3 S2 X 63.75 → 64.5", "Shafts!C4 S3 X 131.75 → 132.5", "Gears!F3 G2 Teeth 68 → 69"):
        check(line in reading.changes, f"the change list says {line}")
    check(desk.a.lay_out_refusal() == "", "the gate is still \"\"")
    desk.say_update()
    u = desk.update
    check(u is not None and not u.needs_new_revision and [p.gear_ids for p in u.changed_parts] == [("G2",)]
          and u.moved_shafts == ("S2", "S3") and set(u.replaced) == {"G2", "G3", "G4"}
          and list(u.ratios) == ["G1 meshes G2"],
          "classify: an Update (the remake): G2's values, S2 and S3 moved, G2, G3 and G4 re-placed, G1 meshes G2 "
          "at 17 : 69")
    desk.say_footer("after the edit")
    guard()
    _, update_result, _ = desk.update_solidworks()
    after_update = stamps(folder, solidworks_only=True)
    changed_files = [n for n in before_update if before_update[n] != after_update.get(n)]
    check(changed_files == [], f"Update SolidWorks saved nothing: SolidWorks files changed on disk {changed_files} "
          f"(of {len(before_update)})")
    check(update_result.ratios == ["G1 meshes G2"] and sorted(update_result.placed) == all_mated(desk),
          f"the gear mate remade and every gear put: ratios {update_result.ratios}, placed {update_result.placed}")
    unsaved = sorted(os.path.basename(p) for p in desk.record.unsaved)
    check(unsaved == ["Gear_m1.5_N68.SLDPRT", "Reducer_12to1.SLDASM", "Reducer_12to1_Layout.SLDPRT"],
          f"the record marks them unsaved: {unsaved}")
    n68 = desk.record.parts[1].path
    sidecar = store.read_sidecar(n68)
    check(sidecar is not None and sidecar.record.unsaved_since > 0 and sidecar.record.spec.get("teeth") == "69",
          f"Gear_m1.5_N68.gear.json says 69 teeth, marked unsaved since {sidecar and sidecar.record.unsaved_since}")
    flags = run(worker, lambda s: save_flags(s, [os.path.join(folder, n) for n in before_update]))
    say(f"        marked modified in SolidWorks right after the update: {flags}")
    check_marks(flags, expected_marks(update_result, desk.record.gearbox.assembly), "a, after the update")
    desk.say_footer("after the update")
    say(f"tag     {ui_text.workbook_built_tag(desk.record, desk.reading.digest)!r}")
    measure_frames(worker, desk, "a updated")
    axes = measure_axes(worker, desk, "a updated")
    off2 = axis_on_line(axes["S2 Axis"], (64.5, 0.0, 0.0), (0.0, 0.0, 1.0))[0]
    off3 = axis_on_line(axes["S3 Axis"], (132.5, 0.0, 0.0), (0.0, 0.0, 1.0))[0]
    check(off2 < 1e-6 and off3 < 1e-6, f"S2 Axis at x 64.5 and S3 Axis at x 132.5 (off {off2:.1e}, {off3:.1e} mm)")
    g1 = next(c for c in desk.record.gearbox.components if c.gear == "G1")
    check(swbuild.same_frame(first["G1"][0], first["G1"][1], g1.rotation, g1.at), "G1 unchanged")
    g2 = next(c for c in desk.record.gearbox.components if c.gear == "G2")
    _, off, _ = frame_error((g2.rotation, g2.at), (wb_layout.IDENTITY, g2.at), 360 / 69)
    check(off < 1e-6, f"G2's turn is now 0 modulo its pitch (69 teeth, odd): off {off:.1e}°")
    values = run(worker, lambda s: live_globals(s, g2.part))
    check(abs(values.get("No. of Teeth", 0) - 69) < 1e-9, f"G2's part {os.path.basename(g2.part)} holds "
          f"\"No. of Teeth\" = {values.get('No. of Teeth')}")
    measure_clear(worker, desk, "a updated")
    measure_mates(worker, desk, "a updated")
    say("        W4's control (G2 put back at its old frame, where the 69-tooth gear clashed with G1) does not hold for "
        "a gear mated to S2 Axis: the axis mate pulls the put back on the next rebuild. The drive at 17 : 69 stands in "
        "for it, showing the assembly turning the 69-tooth G2 (ruled on 2026-11-14)")
    drive_proof(worker, desk, "a updated, at 17 : 69")
    negative_controls(worker, desk, "a updated")

    say("-- a   a structural edit in Excel: G1's bore 8 -> blank")
    guard()
    book.set("Gears", "J2", None)
    book.save()
    desk.poll()
    desk.say_update()
    check(desk.update is not None and desk.update.needs_new_revision, "classify: a new revision is needed")
    check(sorted(os.path.basename(p) for p in desk.record.unsaved) == unsaved,
          "the documents Update changed are still unsaved (nothing saved them)")
    desk.say_plan()
    p = desk.plan
    for m in (p.made_new if p is not None else ()):
        say(f"        made new: {m.why}: {m.sentence}")
    check(p is not None and not p.refusal and p.revision == 2
          and [j.stem for j in p.build] == ["Gear_m1.5_N17_r2", "Gear_m1.5_N69"]
          and sorted(r.stem for r in p.reuse) == ["Gear_m2_N17", "OutputGear"],
          "the plan, with Update's changes unsaved: Reducer_12to1_r2, new parts for G1 (Gear_m1.5_N17_r2) and G2 "
          "(Gear_m1.5_N69), G3 and G4 reused")
    check(p is not None and [(m.gear_ids, os.path.basename(m.old), os.path.basename(m.new))
                             for m in p.unsaved_made_new] == [(("G2",), "Gear_m1.5_N68.SLDPRT", "Gear_m1.5_N69.SLDPRT")],
          "review B2: G2's part is made new because Gear_m1.5_N68 is not saved, and nothing waits for a save")
    say(f"question {ui_text.build_again_question(desk.update, desk.plan, record=desk.record)}")
    f = desk.say_footer("structural, unsaved")
    check(f.build_enabled and f.update_enabled, "neither Build again… nor Update SolidWorks is held by the unsaved "
          "documents")
    guard()
    earlier, earlier_sidecars = stamps(folder), sidecar_texts(folder)
    say(f"stamps  {len(earlier)} earlier files: " + ", ".join(sorted(earlier)))
    _, result = desk.build()
    later = check_earlier_unchanged(folder, earlier, "a build again", earlier_sidecars)
    new = sorted(n for n in later if n not in earlier)
    check(new == ["Gear_m1.5_N17_r2.SLDPRT", "Gear_m1.5_N17_r2.gear.json", "Gear_m1.5_N69.SLDPRT",
                  "Gear_m1.5_N69.gear.json", "Reducer_12to1_r2.SLDASM", "Reducer_12to1_r2_Layout.SLDPRT"],
          f"new files only where needed: {new}")
    check(result is not None and result.kind == store.GEARBOX_MOTION, f"_r2 built turning: "
          f"{result and result.kind!r}")
    rec = desk.record
    check(rec.gearbox.revision == 2 and [e.revision for e in rec.earlier] == [0]
          and [os.path.basename(p) for e in rec.earlier for p in e.parts] == ["Gear_m1.5_N17.SLDPRT",
                                                                              "Gear_m1.5_N68.SLDPRT"],
          "the record: revision 2 current; revision 0 earlier, with the G1 and G2 parts it no longer uses")
    flags = run(worker, lambda s: save_flags(s, [os.path.join(folder, n) for n in earlier if n.endswith(
        (".SLDPRT", ".SLDASM"))]))
    say(f"        marked modified in SolidWorks now (not saved): {flags}")
    check(flags.get("Gear_m1.5_N17.SLDPRT") is False, "the superseded G1 part, which Update never changed, is not "
          "marked modified")
    desk.say_footer("after build again")
    measure(worker, desk, "a _r2")
    book.close()
    return desk


def section_a2(worker, excel):
    say("== a2  a build stopped after the parts and layout, carried on; then Build pressed with nothing changed")
    folder = fresh_folder("a2")
    path = os.path.join(folder, "Reducer_12to1.xlsx")
    shutil.copy2(FIXTURE_12, path)
    book = Workbook(excel, path, "a2")
    book.set("Box", "B4", folder + "\\")
    missing = os.path.join(folder, "No such template.asmdot")
    book.set("Box", "B6", missing)
    book.save()
    desk = Desk(path, worker)
    desk.read()
    desk.say_plan(full=False)
    guard()
    plan, result = desk.build()
    check(not result.ok and result.layout is not None and result.layout.saved and len(result.parts.built) == 4
          and result.assembly is not None and not result.assembly.saved,
          "the build stopped at the assembly: 4 parts and the layout saved, the assembly not made")
    rec = desk.record
    check(rec is not None and rec.gearbox.layout and not rec.gearbox.assembly and rec.digest == "",
          "the record holds the parts and the layout, no assembly, and no digest (it is not built from this read)")
    say(f"tag     {ui_text.workbook_built_tag(desk.record, desk.reading.digest)!r}")
    desk.say_footer("after the stopped build")
    say(f"open    {run(worker, open_titles)}")
    book.set("Box", "B6", None)
    book.save()
    desk.poll()
    desk.say_plan(full=False)
    p = desk.plan
    check(p is not None and p.revision == 0 and not p.build and len(p.reuse) == 4
          and isinstance(p.layout, wb_gearbox.LayoutReuse), "Build carries on: revision 0, 4 parts and the layout "
          "reused, only the assembly to make")
    desk.say_footer("cell cleared")
    guard()
    plan, result = desk.build()
    check(result.ok and len(result.checked) == 5 and result.clashes == [] and result.kind == store.GEARBOX_MOTION,
          f"carried on: checked {[os.path.basename(c) for c in result.checked]}, assembly saved turning, no "
          "interference")
    check(desk.record.digest == desk.reading.digest, "the record now claims this read")
    measure(worker, desk, "a2 carried on", controls=False, again=False)
    PERSON.append(("a2", desk.record.gearbox.assembly))
    desk.say_footer("after carrying on")
    say("-- a2  Build pressed again, nothing changed")
    desk.say_update()
    desk.say_plan(full=False)
    p = desk.plan
    say(f"question {ui_text.build_again_question(desk.update, p, record=desk.record)}")
    check(p is not None and p.revision == 2 and not p.build and len(p.reuse) == 4,
          "the plan: Reducer_12to1_r2 beside it, reusing all 4 parts, a new layout and assembly")
    earlier = stamps(folder)
    guard()
    desk.build()
    later = stamps(folder)
    touched = [n for n in earlier if later.get(n) != earlier[n]]
    check(touched == [], f"every earlier file's sha256 and mtime unchanged: changed {touched}")
    measure(worker, desk, "a2 _r2", controls=False, again=False)
    left = run(worker, close_ours)
    check(not left, f"closed: left {left}")
    book.close()


def section_a3(worker, excel):
    say("== a3  the journal: a build interrupted after two parts saved; then an Update lost when its documents "
        "closed unsaved, typed back")
    folder = fresh_folder("a3")
    path = os.path.join(folder, "Reducer_12to1.xlsx")
    shutil.copy2(FIXTURE_12, path)
    book = Workbook(excel, path, "a3")
    book.set("Box", "B4", folder + "\\")
    book.save()
    desk = Desk(path, worker)
    desk.read()
    plan = desk.plan
    check(plan is not None and plan.revision == 0 and len(plan.build) == 4 and not plan.reuse,
          "the plan: revision 0, four parts to make")

    say("-- a3  the journal written; the job then saves two parts and is never collected")
    check(desk.write_journal(plan), "the journal is on record before the job, as the window writes it")
    say(f"journal {[(os.path.basename(e.path), e.kind) for e in store.read_link_record(path).pending]}")
    two = plan.build[:2]
    guard()
    interrupted = run(worker, lambda s: swbuild.build_many(s, [j.plan for j in two], os.path.exists))
    for line in interrupted.log_lines():
        say("        " + line)
    check(interrupted.ok and all(os.path.isfile(j.path) and store.read_sidecar(j.path) is None for j in two),
          f"SolidWorks saved {[os.path.basename(j.path) for j in two]}, and no .gear.json is beside either: the "
          "finish never ran")
    desk.plan_solidworks()
    desk.say_plan(full=False)
    p = desk.plan
    check(p is not None and p.revision == 0 and p.made_new == ()
          and [r.stem for r in p.reuse] == [j.stem for j in two] and all(r.journaled for r in p.reuse)
          and [j.stem for j in p.build] == [j.stem for j in plan.build[2:]],
          "the next plan reuses the two the journal names, to be checked live, and makes the other two: revision 0, "
          "no suffix, nothing called a file with no record")
    desk.say_footer("after the interrupted build")
    guard()
    _, result = desk.build()
    check(result.ok and result.checked[:2] == [r.path for r in p.reuse] and result.kind == store.GEARBOX_MOTION,
          f"built turning, the two checked live first: {[os.path.basename(c) for c in result.checked]}")
    for r in p.reuse:
        sidecar = store.read_sidecar(r.path)
        check(sidecar is not None and store.same_path(sidecar.record.workbook, path)
              and sidecar.record.trig == result.held.get(r.path) and sidecar.record.variables,
              f"{r.stem}.gear.json written at the finish, for this workbook, in {result.held.get(r.path)!r}")
    check(store.read_link_record(path).pending == [] and len(desk.record.parts) == 4,
          "the journal is taken out, and the four parts are on record")
    measure(worker, desk, "a3 built", controls=False, again=False)

    say("-- a3  S2 X 64.5 and G2 Teeth 69, and Update, left unsaved; then the documents closed without saving")
    n68 = next(e.path for e in desk.record.parts if e.gears == ["G2"])
    book.set("Shafts", "C3", 64.5)
    book.set("Gears", "F3", 69)
    book.save()
    desk.poll()
    desk.say_update()
    guard()
    desk.update_solidworks()
    unsaved = sorted(os.path.basename(x) for x in desk.record.unsaved)
    check("Gear_m1.5_N68.SLDPRT" in unsaved, f"the record marks what Update changed unsaved: {unsaved}")
    check(store.read_sidecar(n68).record.unsaved_since > 0, "Gear_m1.5_N68.gear.json is marked unsaved")
    left = run(worker, quit_in(folder))
    check(not left, f"this section's documents closed in SolidWorks without saving: left {left}")
    desk.plan_solidworks()
    check(sorted(os.path.basename(x) for x in desk.record.unsaved) == unsaved,
          "the marks stay: the files were not saved, and nothing on the Tk thread can see SolidWorks")
    desk.say_footer("documents closed unsaved")
    say(f"tag     {ui_text.workbook_built_tag(desk.record, desk.reading.digest)!r}")
    book.set("Shafts", "C3", 63.75)
    book.set("Gears", "F3", 68)
    book.save()
    desk.poll()
    desk.say_update()
    guard()
    _, result, _ = desk.update_solidworks()
    current = [e.path for e in desk.record.current_parts()] + [desk.record.gearbox.layout,
                                                               desk.record.gearbox.assembly]
    # Ruled on 2026-11-14 (with package A's fix: the check phase reads each recorded gear mate's live ratio): the
    # reopened gear mate already reads 17 : 68, what the workbook now wants, so it is not remade; the parts, the layout
    # and the frames all hold what the file holds, so nothing is changed. The sentence for "the earlier Update was
    # lost and nothing needed making again" is package C's to write after A's fix: logged, not pinned.
    changed = sorted(os.path.basename(x) for x in result.changed)
    check(result.ratios == [] and result.ratios_already == ["G1 meshes G2"] and changed == [],
          f"Update found the gear mate already at 17 : 68 and every document holding the workbook's values: no remake, "
          f"nothing changed: ratios {result.ratios}, ratios_already {result.ratios_already}, changed {changed}")
    check([tuple(r) for r in result.ratios_read] == [("G1 meshes G2", 17, 68, 17, 68)],
          f"Update read the gear mate at 17 : 68, as wanted: ratios_read {result.ratios_read}")
    entry = next(m for m in desk.record.gearbox.mates if m.name == "G1 meshes G2")
    check(list(entry.ratio) == [17, 68], f"the record takes the ratio SolidWorks holds: G1 meshes G2 {entry.ratio}")
    check(desk.note[0] == TYPED_BACK_SENTENCE, f"the sentence (package C, 43527b4): {desk.note[0]!r}")
    check(sorted(os.path.basename(x) for x in result.opened) == sorted(os.path.basename(x) for x in current),
          f"it loaded every document from its file: {[os.path.basename(x) for x in result.opened]}")
    say(f"fact    the marks: unsaved {[os.path.basename(p) for p in desk.record.unsaved]}, mismatched "
        f"{[os.path.basename(p) for p in desk.record.mismatched]}")
    sidecar = store.read_sidecar(n68)
    check(sidecar.record.unsaved_since == 0 and sidecar.record.spec.get("teeth") == "68",
          f"Gear_m1.5_N68.gear.json says 68 teeth, unmarked ({sidecar.record.unsaved_since})")
    say(f"tag     {ui_text.workbook_built_tag(desk.record, desk.reading.digest)!r}")
    drive_proof(worker, desk, "a3 typed back, the gear mate's live ratio 17 : 68")
    book.set("Gears", "J2", None)
    book.save()
    desk.poll()
    desk.say_plan(full=False)
    q = desk.plan
    check(q is not None and n68 in [r.path for r in q.reuse] and not any(store.same_path(m.old, n68)
                                                                       for m in q.made_new),
          "a build-again plan now reuses Gear_m1.5_N68")
    desk.say_footer("structural")
    book.close()


def section_b(worker, excel):
    say("== b   a pure move: S2 placed by formulas from an angle cell, moved along its arc")
    folder = fresh_folder("b")
    path = os.path.join(folder, "Arc_Move.xlsx")
    xlsx.write_new(path, wb_model.to_sheets(spec_arc(folder + "\\")))
    say(f"write   {os.path.basename(path)} by the app's own write_new")
    book = Workbook(excel, path, "b")
    book.set("Shafts", "L1", "Angle (°)")
    book.set("Shafts", "L3", 30)
    book.set("Shafts", "C3", f"={ARC_R:g}*COS(RADIANS(L3))")
    book.set("Shafts", "D3", f"={ARC_R:g}*SIN(RADIANS(L3))")
    book.set("Shafts", "C4", "=C3+40")
    book.set("Shafts", "D4", "=D3")
    keep_fixture(book, "Arc_Move.xlsx", "C:\\Parts\\Arc_Move\\")
    book.set("Box", "B4", folder + "\\")
    book.save()
    desk = Desk(path, worker)
    desk.read()
    check(desk.a.lay_out_refusal() == "", "the gate is \"\"")
    shafts = {s.shaft: s for s in desk.plan_shafts()}
    check(all(shafts[s].x_side == wb_layout.PLUS and shafts[s].y_side == wb_layout.PLUS for s in ("S2", "S3")),
          "S2 and S3 are off both base planes: four layout planes, four globals")
    build_turning(worker, desk, "b", 4)
    measure(worker, desk, "b built")
    guard()
    before = stamps(folder, solidworks_only=True)
    edit(desk, book, ("Shafts", "L3", 40))
    u = desk.update
    check(u is not None and not u.needs_new_revision and not u.changed_parts and u.moved_shafts == ("S2", "S3"),
          "classify: no part values, S2 and S3 moved (layout globals only), and re-places")
    desk.say_footer("after the angle edit")
    guard()
    _, result, _ = desk.update_solidworks()
    check(result.ok and not any(r.changed for r in result.parts) and result.layout is not None
          and sorted(result.layout.changed) == ["S2 X", "S2 Y", "S3 X", "S3 Y"],
          f"Update: no part touched; the layout's S2 X, S2 Y, S3 X, S3 Y set: {result.layout and result.layout.changed}; "
          f"re-placed {result.placed}")
    flags = run(worker, lambda s: save_flags(s, [os.path.join(folder, n) for n in before]))
    say(f"        marked modified in SolidWorks right after the update: {flags}")
    check_marks(flags, ["Arc_Move.SLDASM", "Arc_Move_Layout.SLDPRT"], "b, the move: only the layout and the assembly "
                "(Update left every part as it was)")
    check(result.clashes == [] and not result.interference_error, f"no interference after the move: {result.clashes}")
    after = stamps(folder, solidworks_only=True)
    check([n for n in before if before[n] != after.get(n)] == [], f"Update saved nothing ({len(before)} SolidWorks "
          "files, sha256 and mtime)")
    measure(worker, desk, "b moved")

    say("-- b   a part-only Update, no gear re-placed: G2's bore 8 -> 10")
    guard()
    before = stamps(folder, solidworks_only=True)
    edit(desk, book, ("Gears", "J3", 10))
    u = desk.update
    check(u is not None and not u.needs_new_revision and [p.gear_ids for p in u.changed_parts] == [("G2",)]
          and not u.moved_shafts and not u.replaced,
          "classify: G2's values alone, no shaft moved, no gear re-placed")
    guard()
    _, result, _ = desk.update_solidworks()
    g2_part = next(c.part for c in desk.record.gearbox.components if c.gear == "G2")
    check(result.ok and result.placed == [] and [os.path.basename(p) for p in result.changed]
          == [os.path.basename(g2_part)],
          f"Update: G2's part changed and nothing else: changed {[os.path.basename(p) for p in result.changed]}, "
          f"re-placed {result.placed}")
    unsaved = sorted(os.path.basename(p) for p in desk.record.unsaved)
    check(unsaved == [os.path.basename(g2_part)], f"the record marks G2's part unsaved and not the assembly, which "
          f"holds nothing new: {unsaved}")
    flags = run(worker, lambda s: save_flags(s, [os.path.join(folder, n) for n in before]))
    say(f"        marked modified in SolidWorks right after the update: {flags}")
    check_marks(flags, expected_marks(result, desk.record.gearbox.assembly),
                f"b, part only: G2's part, and the assembly only if Update rebuilt it (rebuilt {result.rebuilt})")
    after = stamps(folder, solidworks_only=True)
    check([n for n in before if before[n] != after.get(n)] == [], "Update saved nothing")
    measure(worker, desk, "b bore", controls=False)
    book.close()


def section_c(worker, excel):
    say("== c   the risky placements: helical across Z+/Z-, herringbones of unequal faces, a helical ring on Z-")
    folder = fresh_folder("c")
    path = os.path.join(folder, "Risky_Placements.xlsx")
    xlsx.write_new(path, wb_model.to_sheets(spec_risky(folder + "\\")))
    say(f"write   {os.path.basename(path)} by the app's own write_new")
    book = Workbook(excel, path, "c")
    keep_fixture(book, "Risky_Placements.xlsx", "C:\\Parts\\Risky_Placements\\")
    book.set("Box", "B4", folder + "\\")
    book.save()
    desk = Desk(path, worker)
    desk.read()
    check(desk.a.lay_out_refusal() == "", "the gate is \"\"")
    build_turning(worker, desk, "c", 6, RING_TURNED_ROUND)
    measure(worker, desk, "c built")
    book.close()


# == W6: right-angle and crossed gearboxes (W6-PLAN §5, §6) ===================================================
#
# Every W6 section goes through the app's own code as W5's do, on the committed findings only. The checks it adds
# (W6-PLAN §6.1, W6-INTERFACES §7.17): frames against layout.frames for any axis; each layout axis on its shaft's
# line; the drive against the base plane square to the input's u₀, the input's turn measured; every gear mate's read
# logged after the build, after each Flip of a control and after a reopen; review M2's interference judge after every
# control drive on a turned mesh; a quiet Update on every built turned gearbox; on 2024 nothing about which Flip is
# right is assumed (it is logged, and the app's read and the drive must agree with each other).

# -- building once, and starting later sections from a copy (W6-PLAN §6.2; W6-INTERFACES §4, pinned) -------------


class CopyStop(Exception):
    """A step of copy_built failed, said in the sentence: the section builds its fixture fresh instead."""


COPY = {"ok": True, "probed": False, "why": ""}   # the copy route; dropped for the run if §7.1's open shows a dialog
CURRENT = {"worker": None}                        # the run's worker, for copy_built's open (its signature is pinned)
MASTER_SUFFIX = ".master"
COPY_TIMEOUT = 120.0                              # W6-PLAN §7.1: the first copied assembly's open, at most


def under(path, folder):
    """Whether ``path`` lies in ``folder``: matched with a separator, so ``…\\r1`` never takes ``…\\r10`` (§7.10)."""
    root = os.path.normcase(os.path.abspath(folder)).rstrip("\\/")
    return bool(path) and os.path.normcase(os.path.abspath(path)).startswith(root + os.sep)


def open_names(session):
    """The file name of every open document (its path's, or its title): compared, never logged."""
    out = []
    for doc in documents(session._app):  # noqa: SLF001
        path = str(call(doc, "GetPathName") or "")
        out.append(os.path.basename(path) if path else str(call(doc, "GetTitle")))
    return out


def folder_flags(session, folder):
    """GetSaveFlag of every open document in ``folder``, by file name."""
    return {os.path.basename(str(call(d, "GetPathName"))): bool(call(d, "GetSaveFlag"))
            for d in documents(session._app) if under(str(call(d, "GetPathName") or ""), folder)}  # noqa: SLF001


def save_modified_in(folder):
    """A worker job: every open document in ``folder`` that SolidWorks holds modified saved (W5's close_ours on 2024)."""
    def work(session):
        saved = []
        for doc in documents(session._app):  # noqa: SLF001
            path = str(call(doc, "GetPathName") or "")
            if under(path, folder) and call(doc, "GetSaveFlag"):
                call(call(doc, "Extension"), "SaveAs3", path, 0, 1, swcom._null_dispatch(),  # noqa: SLF001
                     swcom._null_dispatch(), swcom._out_long(), swcom._out_long())  # noqa: SLF001
                saved.append(os.path.basename(path))
        return saved
    return work


def end_clean(worker, folder, label, rename, save=True):
    """copy_built's step 1 (``rename``: the builder section's end, run once, W6-INTERFACES §7.9) or step 4 (a copy
    section's end, without the rename): every document of the folder closed (``quit_in``; on 2024 this run's modified
    documents saved first, as W5's close_ours), Excel's workbook closed (``close_books``), no open document by a file
    name the folder holds; then the folder renamed ``<section>.master``, which it stays for the rest of the run.
    Returns the folder it leaves (the master's with the rename)."""
    if TAG["major"] == 32 and save:
        saved = run(worker, save_modified_in(folder))
        say(f"        {label}: SolidWorks 2024, this run's modified documents saved before the close: {saved}")
    left = run(worker, quit_in(folder))
    books = close_books()
    held = {n.lower() for n in os.listdir(folder)}
    same = sorted({n for n in run(worker, open_names) if n.lower() in held})
    ok = not left and not same
    check(ok, f"{label}: {os.path.basename(folder)} ends clean: every document of it closed in SolidWorks (left "
              f"{left}), Excel's workbook closed ({books}), no open document by a file name it holds ({same})")
    if not ok:
        raise CopyStop(f"{os.path.basename(folder)} did not end clean: left {left}, open by its file names {same}")
    if not rename:
        return folder
    master, last = folder + MASTER_SUFFIX, None
    for _ in range(20):                   # a file SolidWorks or Excel let go of a moment ago
        try:
            os.rename(folder, master)
            break
        except OSError as exc:
            last = exc
            time.sleep(0.5)
    else:
        raise CopyStop(f"{os.path.basename(folder)} could not be renamed {os.path.basename(master)}: {last}")
    say(f"master  {os.path.basename(folder)} renamed {os.path.basename(master)}: it stays so for the rest of the run")
    return master


def keep_master(worker, folder, section):
    """The builder section's end: ``end_clean`` with the rename; a failure said, and the copy route dropped."""
    try:
        return end_clean(worker, folder, f"{section}, the builder's end", True)
    except CopyStop as exc:
        check(False, f"{section}: the master was not kept ({exc}); every later section builds its fixture fresh")
        COPY.update(ok=False, why=str(exc))
        return ""


def end_copy(worker, folder, section, save=True):
    """A copy section's end (copy_built step 4): two copies are never open together. ``save`` False: nothing is saved
    first on 2024 either (p2's second ring mate is never saved)."""
    try:
        end_clean(worker, folder, f"{section}, the copy's end", False, save=save)
    except CopyStop as exc:
        check(False, f"{section}: {exc}")


def rewrite_paths(value, old, new, changed, where):
    """Every string in a record — fields of dataclasses, items of lists, tuples and dicts, and dict keys — that starts
    with the folder ``old`` followed by a separator (normcase), put onto ``new`` (W6-INTERFACES §4 step 2, §7.10);
    ``changed`` collects where each was. Dataclasses are changed in place; the rest is returned."""
    if isinstance(value, str):
        n, o = os.path.normcase(value), os.path.normcase(old).rstrip("\\/")
        if len(n) > len(o) and n.startswith(o) and n[len(o)] in "\\/":
            changed.append(where)
            return new.rstrip("\\/") + value[len(o):]
        return value
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        for f in dataclasses.fields(value):
            object.__setattr__(value, f.name, rewrite_paths(getattr(value, f.name), old, new, changed,
                                                            f"{where}.{f.name}"))
        return value
    if isinstance(value, list):
        return [rewrite_paths(v, old, new, changed, f"{where}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, tuple):
        return tuple(rewrite_paths(v, old, new, changed, f"{where}[{i}]") for i, v in enumerate(value))
    if isinstance(value, dict):
        return {rewrite_paths(k, old, new, changed, f"{where} key"): rewrite_paths(v, old, new, changed,
                                                                                 f"{where}[{k!r}]")
                for k, v in value.items()}
    return value


def strings_in(value, where=""):
    """(where, text) for every string in a record, as ``rewrite_paths`` walks it."""
    if isinstance(value, str):
        yield where, value
    elif dataclasses.is_dataclass(value) and not isinstance(value, type):
        for f in dataclasses.fields(value):
            yield from strings_in(getattr(value, f.name), f"{where}.{f.name}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            yield from strings_in(v, f"{where}[{i}]")
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from strings_in(k, f"{where} key")
            yield from strings_in(v, f"{where}[{k!r}]")


def absolute(text):
    import ntpath
    return bool(text) and (ntpath.isabs(text) and (len(text) > 2 and text[1] == ":" or text.startswith("\\\\"))
                           or (os.sep == "/" and os.path.isabs(text)))


def copy_built(master: str, section: str) -> str:
    """W6-INTERFACES §4, pinned (W7's demonstration reuses it): the kept master folder copied to ``OUT/<section>`` and
    made valid there; returns the copy's folder. Step 1 (the builder's clean end and the rename) ran once at the
    builder's end (``keep_master``), step 4 is ``end_copy``. A step that fails raises CopyStop with its sentence."""
    worker = CURRENT["worker"]
    if not master.endswith(MASTER_SUFFIX) or not os.path.isdir(master):
        raise CopyStop(f"{master} is not a kept master folder (one renamed to end {MASTER_SUFFIX})")
    old, copy = master[:-len(MASTER_SUFFIX)], os.path.join(OUT, section)
    if os.path.exists(copy):
        raise SystemExit(f"{copy} exists already; give a fresh output folder")
    # 2. The copy, its records put onto it through store's own reader and writer.
    shutil.copytree(master, copy)                 # copy2: the mtimes kept
    say(f"copy    {os.path.basename(master)} -> {section}: {len(os.listdir(copy))} files, mtimes kept")
    records = []
    for name in sorted(os.listdir(copy)):
        workbook = os.path.join(copy, name)
        if not name.lower().endswith(".xlsx") or name.startswith("~$") or not os.path.exists(
                store.link_record_path(workbook)):
            continue
        record, changed = store.read_link_record(workbook), []
        rewrite_paths(record, old, copy, changed, "record")
        store.save_link_record(record, store.link_record_path(workbook))
        say(f"        {name}'s record: {len(changed)} path(s) put onto the copy: {changed}")
        records.append(workbook)
    for name in sorted(os.listdir(copy)):
        if name.endswith(store.SIDECAR_SUFFIX):
            path = os.path.join(copy, name)
            sidecar, changed = store.read_sidecar(path), []
            if sidecar is None:
                raise CopyStop(f"{name} in the copy could not be read by store.read_sidecar")
            rewrite_paths(sidecar, old, copy, changed, "sidecar")
            store.save(path, sidecar)
            say(f"        {name}: {len(changed)} path(s) put onto the copy: {changed}")
    if not records:
        raise CopyStop(f"{os.path.basename(master)} holds no workbook with a record")
    for workbook in records:
        record = store.read_link_record(workbook)
        owner = store.record_owner(record, workbook)
        behind, missing, elsewhere = [], [], []
        for where, text in strings_in(record, "record"):
            if not absolute(text):
                continue
            if under(text, old) or os.path.normcase(text).rstrip("\\/") == os.path.normcase(old):
                behind.append(where)
            elif under(text, copy):
                if not os.path.exists(text):
                    missing.append(where)
            else:
                elsewhere.append(where)
        marks = (sorted(record.unsaved), sorted(record.mismatched))
        dropped = store.clear_saved(record)
        digest = wb_link.Link(workbook).read().digest
        ok = owner[0] == store.OURS and not behind and not missing and not dropped and digest == record.digest
        if elsewhere:
            say(f"fact    {section}: paths in the record outside the copy (not the folder's): {elsewhere}")
        check(ok, f"{section}: the copy's record is valid: owner {owner}; left on the master {behind}; missing in "
                  f"the copy {missing}; clear_saved dropped {'something' if dropped else 'nothing'} (unsaved, "
                  f"mismatched {marks}); the read's digest {'equals' if digest == record.digest else 'differs from'} "
                  "the record's")
        if not ok:
            raise CopyStop(f"the copy's record of {os.path.basename(workbook)} is not valid in {section}")
    # 3. SolidWorks finds the copy's files.
    copy_opens(worker, copy, section, records)
    return copy


def copy_opens(worker, copy, section, records):
    """copy_built step 3: the copy's assembly opened once (the app's own open: OpenDoc6, silent), every component's
    and the layout's path read, the flags straight after the open logged as facts, the assembly closed without saving
    (QuitDoc). The run's first copy opens under the dialog watch with a 120 s timeout (W6-PLAN §7.1): a dialog drops
    the copy route for the rest of the run; no answer in the time stops the run (the worker is held)."""
    for workbook in records:
        box = store.read_link_record(workbook).gearbox
        if box is None or not box.assembly:
            continue
        names = [c.name for c in box.components] + [box.layout_component]

        def work(s):
            found = {}
            for index, name in enumerate(names):
                s.find_component(f"copy{index}", name)
                found[name] = s.component_path(f"copy{index}")
            return found
        held = {n.lower() for n in os.listdir(copy)}
        same = sorted({n for n in run(worker, open_names) if n.lower() in held})
        if same:               # W7-PLAN §6 (review S13): no open document may share a file name with the copy's
            raise CopyStop(f"documents open in SolidWorks share the copy's file names: {same}")
        first = not COPY["probed"]
        if first:
            OPEN_DIALOGS.clear()
            OPENING.set()
            say(f"probe   W6-PLAN §7.1: {os.path.basename(box.assembly)} of {section}, whose stored references name a "
                f"folder that is gone, opened under the dialog watch ({COPY_TIMEOUT:g} s at most)")
        started = time.monotonic()
        try:
            paths = run(worker, in_assembly(box.assembly, work), timeout=COPY_TIMEOUT if first else 600)
        except queue.Empty:
            raise Halt(f"{section}: the copied assembly did not open in {COPY_TIMEOUT:g} s (W6-PLAN §7.1); the "
                       f"worker is held, so the run stops; dialogs seen {OPEN_DIALOGS}") from None
        except (Halt, Stopped):
            raise
        except Exception as exc:  # noqa: BLE001 - the open's own sentence, and the section builds fresh
            raise CopyStop(f"the copy's assembly would not open: {type(exc).__name__}: {exc}") from None
        finally:
            if first:
                OPENING.clear()
                COPY["probed"] = True
        flags = run(worker, lambda s: folder_flags(s, copy))
        say(f"fact    {section}: the copy's assembly opened in {time.monotonic() - started:.1f} s; marked modified "
            f"straight after the open: {flags}")
        left = run(worker, quit_in(copy))
        if first:
            say(f"fact    W6-PLAN §7.1: dialogs while the copied assembly opened: {OPEN_DIALOGS or 'none'}")
            if OPEN_DIALOGS:
                COPY.update(ok=False, why=f"a dialog appeared while a copied assembly opened: {OPEN_DIALOGS}")
                raise CopyStop(COPY["why"])
        strays = {n: p for n, p in paths.items() if not under(p, copy)}
        check(not strays and not left, f"{section}: SolidWorks found all {len(paths)} components and the layout in "
              f"the copy, and the copy closed without saving (left {left}): elsewhere {strays or 'none'}")
        if strays:
            raise CopyStop(f"a copy loaded the master's files: {strays}")


def start_copy(worker, excel, section, builder, spec):
    """A copy section's start (W6-PLAN §6.2): ``copy_built`` of ``<builder>.master`` read through the window's own
    path, or — no master in this run, the copy route dropped, or a step of the copy stopped — the fixture written
    and built fresh in the section's folder, as W5's sections start."""
    master = os.path.join(OUT, builder + MASTER_SUFFIX)
    if COPY["ok"] and os.path.isdir(master):
        try:
            folder = copy_built(master, section)
        except CopyStop as exc:
            check(False, f"{section}: the copy of {builder}{MASTER_SUFFIX} STOPPED: {exc}; the section builds its "
                         "fixture fresh")
            stopped = os.path.join(OUT, section)
            if os.path.exists(stopped):
                os.rename(stopped, stopped + ".copy-stopped")
        else:
            path = os.path.join(folder, f"{spec('').box.name}.xlsx")
            book = Workbook(excel, path, section)
            desk = Desk(path, worker, strip=folder)
            desk.read()
            box = desk.record.gearbox if desk.record is not None else None
            check(turning(desk) and desk.record.digest == desk.reading.digest and under(box.assembly, folder),
                  f"{section}: the copy reads as built from this workbook, its gearbox in the copy: "
                  f"{box and os.path.basename(os.path.dirname(box.assembly))}")
            desk.say_update()
            desk.say_footer(f"{section}, the copy read")
            return folder, path, book, desk
    else:
        say(f"fresh   {section}: {'no ' + builder + MASTER_SUFFIX + ' in this run' if COPY['ok'] else 'the copy route was dropped: ' + COPY['why']}; "
            "the fixture is built fresh")
    folder, path, book, desk = write_fixture(worker, excel, section, spec)
    build_turning(worker, desk, f"{section}, built fresh", None, None)
    return folder, path, book, desk


# -- the fixtures (W6-PLAN §5): written by write_new, saved once by Excel, Output folder blank ----------------


def spec_bevel_reducer(folder=""):
    """Fixture A, ``Bevel_Reducer`` (§5.1): a bevel stage at 90° (S1 on X+ into S2 on Z+) feeding a parallel stage."""
    return GearboxSpec(
        box=Box(name="Bevel_Reducer", output_folder=folder),
        shafts=(Shaft("S1", "frame", "0", "0", "60", "X+", "input", speed="1500", torque="10"),
                Shaft("S2", "frame", "0", "0", "0", "Z+"),
                Shaft("S3", "frame", "-68", "0", "0", "Z+", "output")),
        gears=(Gear("G1", "S1", "0", "bevel", "external", "20", "3", face_width="20", bore="10"),
               Gear("G2", "S2", "60", "bevel", "external", "40", "3", face_width="20", bore="10"),
               Gear("G3", "S2", "5", "spur", "external", "17", "2", face_width="10", bore="8"),
               Gear("G4", "S3", "5", "spur", "external", "51", "2", face_width="10", bore="8")),
        meshes=(Mesh("G1", "G2"), Mesh("G3", "G4")))


def spec_crossed_slant(folder=""):
    """Fixture B, ``Crossed_Slant`` (§5.2): a crossed helical stage (S1 Z+, S2 X+, skew at 90°), then a bevel stage at
    120° onto the slanted S3."""
    return GearboxSpec(
        box=Box(name="Crossed_Slant", output_folder=folder),
        shafts=(Shaft("S1", "frame", "0", "0", "0", "Z+", "input", speed="1000", torque="5"),
                Shaft("S2", "frame", "0", "84.852814", "8", "X+"),
                Shaft("S3", "frame", "-110", "84.852814", "8", "-1, 1.732050807569, 0", "output")),
        gears=(Gear("G1", "S1", "10", "helical", "external", "20", "2", face_width="16", bore="6", helix_angle="45",
                    hand="right"),
               Gear("G2", "S2", "0", "helical", "external", "40", "2", face_width="16", bore="8", helix_angle="45",
                    hand="right"),
               Gear("G3", "S2", "-110", "bevel", "external", "20", "2.5", face_width="10", bore="8"),
               Gear("G4", "S3", "0", "bevel", "external", "30", "2.5", face_width="10", bore="8")),
        meshes=(Mesh("G1", "G2"), Mesh("G3", "G4")))


def spec_bevel_reducer_y(folder=""):
    """Fixture A turned onto a Y input (W6-INTERFACES §7.17's addition): S1 along Y+ through (0, 0, 60), S2 and S3 30
    mm to −Y, G1 at At −30, so G1's cone tip (−30 along Y) sits on the minus side of the Top plane: its along mate is
    a point distance to Top with a negative coordinate, which only the fake has shown (W5 probed Front alone)."""
    return GearboxSpec(
        box=Box(name="Bevel_Reducer_Y", output_folder=folder),
        shafts=(Shaft("S1", "frame", "0", "0", "60", "Y+", "input", speed="1500", torque="10"),
                Shaft("S2", "frame", "0", "-30", "0", "Z+"),
                Shaft("S3", "frame", "-68", "-30", "0", "Z+", "output")),
        gears=(Gear("G1", "S1", "-30", "bevel", "external", "20", "3", face_width="20", bore="10"),
               Gear("G2", "S2", "60", "bevel", "external", "40", "3", face_width="20", bore="10"),
               Gear("G3", "S2", "5", "spur", "external", "17", "2", face_width="10", bore="8"),
               Gear("G4", "S3", "5", "spur", "external", "51", "2", face_width="10", bore="8")),
        meshes=(Mesh("G1", "G2"), Mesh("G3", "G4")))


def spec_crossed_stage(folder=""):
    """Fixture B's crossed stage alone, moved 10 mm up (the review's M4 move, as tests' ``crossed_off_base``), so S1 can
    pass to the other side of S2 without crossing the Top plane: the crossed mesh's sense flips."""
    return GearboxSpec(
        box=Box(name="Crossed_Stage", output_folder=folder),
        shafts=(Shaft("S1", "frame", "0", "10", "0", "Z+", "input", speed="1000", torque="5"),
                Shaft("S2", "frame", "0", "94.852814", "8", "X+", "output")),
        gears=(Gear("G1", "S1", "10", "helical", "external", "20", "2", face_width="16", bore="6", helix_angle="45",
                    hand="right"),
               Gear("G2", "S2", "0", "helical", "external", "40", "2", face_width="16", bore="8", helix_angle="45",
                    hand="right")),
        meshes=(Mesh("G1", "G2"),))


INVOLUTE = "above the form diameter of {}, so the bottom of the working flank is a straight line."
# The expected Checks panels, speeds and torques (W6-PLAN §5.1, §5.2), each warning with its cell.
A_EXPECT = {
    "warnings": ["Gears!F2: G1: The tooth tip is 0.722 mm thick, under 0.3 × module (0.9 mm).",
                 "Gears!Q2: G1: The involute starts at 65.444 mm, " + INVOLUTE.format("63.267 mm"),
                 "Gears!Q5: G4: The involute starts at 99.28 mm, " + INVOLUTE.format("98.614 mm")],
    "header": "Bevel and parallel train · 2 meshes · 6.000 : 1 · output at 90° to the input",
    "speeds": {"S1": 1500.0, "S2": -750.0, "S3": 250.0},
    "torques": {"S1": 10.0, "S2": 19.6, "S3": 57.624},
    "seen": {"S1": "+X", "S2": "+Z", "S3": "+Z"},
    "kinds": {("G1", "G2"): "bevel", ("G3", "G4"): "parallel"},
    "speed_texts": ["1500.0 rpm anticlockwise", "750.0 rpm clockwise", "250.0 rpm anticlockwise"],
    "lines": ["S1    1500.0\u00a0rpm anticlockwise seen from the +X end · 10.00\u00a0N·m",
              "S2    750.0\u00a0rpm clockwise seen from the +Z end · 19.60\u00a0N·m",
              "S3    250.0\u00a0rpm anticlockwise seen from the +Z end · 57.62\u00a0N·m"]}
A_Y_EXPECT = dict(A_EXPECT, seen={"S1": "+Y", "S2": "+Z", "S3": "+Z"},
                  lines=[A_EXPECT["lines"][0].replace("+X end", "+Y end")] + A_EXPECT["lines"][1:])
B_EXPECT = {
    "warnings": ["Gears!Q2: G1: The involute starts at 53.849 mm, " + INVOLUTE.format("53.14 mm"),
                 "Gears!L2: G1: A helix angle of 45° is outside the usual 8–30° for a helical gear.",
                 "Gears!Q3: G2: The involute starts at 110.417 mm, " + INVOLUTE.format("109.413 mm"),
                 "Gears!L3: G2: A helix angle of 45° is outside the usual 8–30° for a helical gear.",
                 "Gears!F4: G3: The tooth tip is 0.664 mm thick, under 0.3 × module (0.75 mm).",
                 "Gears!Q4: G3: The involute starts at 64.97 mm, " + INVOLUTE.format("62.668 mm")],
    "header": "Crossed and bevel train · 2 meshes · 3.000 : 1 · output at 90° to the input",
    "speeds": {"S1": 1000.0, "S2": 500.0, "S3": -1000.0 / 3},
    "torques": {"S1": 5.0, "S2": 9.8, "S3": 14.406},
    "seen": {"S1": "+Z", "S2": "+X", "S3": "(0.5, −0.866, 0)"},
    "kinds": {("G1", "G2"): "crossed", ("G3", "G4"): "bevel"},
    "speed_texts": ["1000.0 rpm anticlockwise", "500.0 rpm anticlockwise", "333.3 rpm anticlockwise",
                    "(0.5, −0.866, 0)"],
    "lines": ["S1    1000.0\u00a0rpm anticlockwise seen from the +Z end · 5.00\u00a0N·m",
              "S2    500.0\u00a0rpm anticlockwise seen from the +X end · 9.80\u00a0N·m",
              "S3    333.3\u00a0rpm anticlockwise seen from the (0.5,\u00a0−0.866,\u00a00) end · 14.41\u00a0N·m"]}
# Each gear's turn for +30° of G1 (W6-PLAN §5), the input's own sign: worked by hand there, held against the app's
# kinematics before every build and Update that changes the ratio.
A_DRIVE = {"G1": 30.0, "G2": -15.0, "G3": -15.0, "G4": 5.0}
A_DRIVE_21 = {"G1": 30.0, "G2": -15.75, "G3": -15.75, "G4": 5.25}             # r3: G1 20 -> 21
B_DRIVE = {"G1": 30.0, "G2": 15.0, "G3": 15.0, "G4": -10.0}
B_DRIVE_31 = {"G1": 30.0, "G2": 15.0, "G3": 15.0, "G4": -15.0 * 20 / 31}      # r6: G4 30 -> 31
B_DRIVE_21_39 = {"G1": 30.0, "G2": 30.0 * 21 / 39, "G3": 30.0 * 21 / 39,      # r8: G1 20 -> 21, G2 40 -> 39
                 "G4": -30.0 * 21 / 39 * 20 / 30}


def write_fixture(worker, excel, section, spec, keep=""):
    """A W6 fixture written by the app's own ``write_new`` with its Output folder blank, saved once by Excel (W6-PLAN
    §5), read with the section's folder as the strip's (as ``WorkbookWindow._folder``); ``keep``: its name under
    ``--fixtures``, copied as Excel saved it."""
    folder = fresh_folder(section)
    made = spec("")
    path = os.path.join(folder, f"{made.box.name}.xlsx")
    xlsx.write_new(path, wb_model.to_sheets(made))
    say(f"write   {os.path.basename(path)} by the app's own write_new, its Output folder blank (the strip's is {folder})")
    book = Workbook(excel, path, section)
    book.save()
    if keep and FIXTURES:
        os.makedirs(FIXTURES, exist_ok=True)
        shutil.copy2(path, os.path.join(FIXTURES, keep))
        say(f"fixture {keep} copied as Excel saved it, its Output folder blank")
    desk = Desk(path, worker, strip=folder)
    desk.read()
    return folder, path, book, desk


def expect_read(desk, label, expect):
    """The read against W6-PLAN §5: the Checks panel exactly (each warning with its cell, no error, nothing more),
    the header, every shaft's speed and torque about its own axis, the end each is seen from, each mesh's kind; the
    Speeds lines logged and their numbers looked for."""
    a = desk.a
    got = sorted(d.message for d in a.diagnostics if d.level == "warning")
    errors = [d.message for d in a.diagnostics if d.level == "error"]
    check(got == sorted(expect["warnings"]) and not errors and a.lay_out_refusal() == "",
          f"{label}: the Checks panel is §5's ({len(expect['warnings'])} warnings, no error): extra "
          f"{sorted(set(got) - set(expect['warnings']))}, missing {sorted(set(expect['warnings']) - set(got))}, "
          f"errors {errors}, gate {a.lay_out_refusal()!r}")
    check(a.report.worked_out_as == expect["header"], f"{label}: the header {a.report.worked_out_as!r}")
    motion = a.report.motion
    speeds = {k: float(v) for k, v in motion.speeds.items()}
    check(speeds.keys() == expect["speeds"].keys() and all(
        abs(speeds[k] - v) <= 1e-9 * max(1.0, abs(v)) for k, v in expect["speeds"].items()),
          f"{label}: the speeds about each shaft's own axis are §5's: {speeds}")
    torques = {k: float(v) for k, v in motion.torques.items()}
    check(all(k in torques and abs(torques[k] - v) <= 1e-9 * max(1.0, abs(v)) for k, v in expect["torques"].items()),
          f"{label}: the torques are §5's: {torques}")
    seen = dict(getattr(motion, "seen_from", {}) or {})
    check(seen == expect["seen"], f"{label}: each shaft seen from its own + end: {seen}")
    kinds = {tuple(k): v.kind for k, v in a.report.meshes.items()}
    check(kinds == expect["kinds"], f"{label}: the meshes' kinds {kinds}")
    lines, readout = ui_text.workbook_speed_lines(a.spec, motion)
    for line in lines:
        say(f"speeds  {line}")
    say(f"speeds  readout {readout!r}")
    text = "\n".join(lines).replace("\u00a0", " ")      # the unit is held to its number by a no-break space
    check(all(t in text for t in expect["speed_texts"]), f"{label}: the Speeds lines carry {expect['speed_texts']}")
    check(lines == expect["lines"], f"{label}: the Speeds lines are C's exactly (W6-INTERFACES §7.19)")


def pin_drive(desk, label, want, input_gear="G1"):
    """The app's kinematics against the turns W6-PLAN §5 works by hand, for +30° of the input, to 1e-9 relative."""
    got = expected_turns(desk, list(want), input_gear, 30.0, 1)
    check(all(abs(got[g] - v) <= 1e-9 * max(1.0, abs(v)) for g, v in want.items()),
          f"{label}: the kinematics give the plan's turns for +30° of {input_gear}: "
          + ", ".join(f"{g} {got[g]:+.9f}° (plan {v:+.9f}°)" for g, v in want.items()))


def say_along(worker, desk, label):
    """Each along mate as the record holds it (plane, signed coordinate, its global) and the assembly global's value
    read from SolidWorks; the frames say whether each gear stands where the plan puts it."""
    box = desk.record.gearbox
    values = run(worker, lambda s: live_globals(s, box.assembly))
    for m in desk.plan.motion.mates if desk.plan is not None and desk.plan.motion is not None else ():
        if m.kind == "along":
            say(f"fact    {label}: {m.name}: plane {getattr(m, 'plane', '')!r}, coordinate {m.z_front:g}, global "
                f"{m.face_global!r} = {values.get(m.face_global) if m.face_global else '(coincident)'}")
    return values


def quiet_update(worker, desk, label):
    """W6-INTERFACES §7.17 (b): Update pressed with nothing changed on a built turned gearbox, saved first so every
    document reads GetSaveFlag False. Its check phase reads every gear mate's sense; nothing may be marked: every
    document's GetSaveFlag read before and after the press, every frame read from SolidWorks unchanged."""
    save_assembly(worker, desk, f"{label}: before the press, so any mark after it is the press's own")
    desk.plan_solidworks()
    desk.say_update()
    frames_before, flags_before = gear_frames(worker, desk), gearbox_flags(worker, desk)
    guard()
    _, result, _ = desk.update_solidworks()
    if result is None:
        return check(False, f"{label}: Update refused: {desk.note[0]}")
    wrong = list(getattr(result, "sense_found_wrong", []) or [])
    resensed = list(getattr(result, "resensed", []) or [])
    check(result.ok and result.placed == [] and result.changed == [] and result.ratios == [] and not wrong
          and not resensed, f"{label}: nothing to do: placed {result.placed}, changed "
          f"{[os.path.basename(p) for p in result.changed]}, ratios {result.ratios}, resensed {resensed}, sense found "
          f"wrong {wrong}")
    check_quiet_update(worker, desk, result, label, frames_before, flags_before)
    desk.say_footer(f"{label}, after the press")
    return result


def built_and_proved(worker, desk, label, parts, controls):
    """A W6 fixture built fresh and judged (W6-PLAN §6.1 r1/r5): built to turn (which Flip each gear mate kept is
    logged on every version); every gear mate's read; §4.1 with the half-pitch controls on every mesh; the drive with
    the both-Flips control and the interference judge on each mesh in ``controls``; a quiet Update; reopened, read,
    and driven with each control again."""
    build_turning(worker, desk, label, parts, None)
    mate_readings(worker, desk, f"{label} built")
    measure(worker, desk, f"{label} built", controls=True, again=False)
    for control in controls:
        drive_proof(worker, desk, f"{label} built, control on {control[0]} meshes {control[1]}", control=control)
    quiet_update(worker, desk, f"{label} quiet Update")
    reopen(worker, desk, f"{label} built")
    mate_readings(worker, desk, f"{label} reopened")
    for control in controls:
        drive_proof(worker, desk, f"{label} reopened, control on {control[0]} meshes {control[1]}", control=control)


def remake_update(worker, desk, book, label, cells, mate, want, folder, globals_wanted=()):
    """W6-INTERFACES §7.17 (a): a tooth change that keeps the mesh valid, by Update: the gear mate ``mate`` made again
    at its new ratio and read back by the committed rule (turned round or not, logged); every gear put; the marks;
    ``globals_wanted`` ((gear whose part, global, value)) read from SolidWorks; every gear mate's read; frames, mates,
    interference, the half-pitch controls; the drive at the new ratio with the both-Flips control and the
    interference judge on the remade mate; a quiet Update (saved first); reopened, read, driven again."""
    say(f"-- {label}: Excel {[(c[0] + '!' + c[1], c[2]) for c in cells]} -> Update: {mate} made again at its new ratio")
    edit(desk, book, *cells)
    u = desk.update
    desk.say_footer(f"{label}, after the edit")
    if u is None or u.needs_new_revision or u.refusal:
        say(f"fact    {label}: not an Update: structural {u and list(u.structural)}; refusal {u and u.refusal!r}")
        check(False, f"{label}: the tooth change is an Update that remakes {mate}")
        return None
    check(list(u.ratios) == [mate] and not list(getattr(u, "resensed", ()) or ()),
          f"classify: an Update remaking {mate} alone: ratios {list(u.ratios)}, resensed "
          f"{list(getattr(u, 'resensed', ()) or ())}")
    pin_drive(desk, label, want)
    guard()
    _, result, _ = desk.update_solidworks()
    if result is None:
        check(False, f"{label}: the Update refused: {desk.note[0]!r}")
        return None
    say(f"fact    {label}: the remake: ratios {result.ratios}, read {result.ratios_read}, turned round "
        f"{getattr(result, 'turned_round', None)}, sense found wrong {getattr(result, 'sense_found_wrong', None)}, "
        f"resensed {getattr(result, 'resensed', None)}, restored {result.restored}")
    check(result.ok and result.ratios == [mate] and sorted(result.placed) == all_mated(desk),
          f"{label}: {mate} made again at its new ratio, every gear put: ratios {result.ratios}, placed "
          f"{result.placed}; {desk.note[0]!r}")
    update_marks(worker, desk, result, label, folder)
    box = desk.record.gearbox
    for gear, name, value in globals_wanted:
        part = next(c.part for c in box.components if c.gear == gear)
        values = run(worker, lambda s, p=part: live_globals(s, p))
        check(abs(float(values.get(name, float("nan"))) - value) < 1e-9, f"{label}: {gear}'s {name!r} reads {value:g} "
              f"in SolidWorks: {values.get(name)}")
    mate_readings(worker, desk, f"{label}, remade")
    measure_frames(worker, desk, label)
    measure_mates(worker, desk, label)
    measure_clear(worker, desk, label)
    negative_controls(worker, desk, label)
    drive_proof(worker, desk, f"{label}, at the new ratio", control=tuple(mate.split(" meshes ")))
    quiet_update(worker, desk, f"{label}, quiet Update")
    reopen(worker, desk, label)
    mate_readings(worker, desk, f"{label}, reopened")
    drive_proof(worker, desk, f"{label}, reopened, at the new ratio")
    return result


# -- the W6 sections (W6-PLAN §6.1) ----------------------------------------------------------------------------


def section_r1(worker, excel):
    say("== r1  fixture A, Bevel_Reducer (W6-PLAN §5.1): a bevel stage at 90° feeding a parallel stage, built fresh; "
        "§4.1, the drive from the Top plane (an X input), both Flips on G1 meshes G2 with the interference judge, a "
        "quiet Update, reopen; then kept as r1.master")
    folder, path, book, desk = write_fixture(worker, excel, "r1", spec_bevel_reducer, keep="Bevel_Reducer.xlsx")
    expect_read(desk, "r1", A_EXPECT)
    pin_drive(desk, "r1", A_DRIVE)
    built_and_proved(worker, desk, "r1", 4, [("G1", "G2")])
    say_along(worker, desk, "r1")
    master = keep_master(worker, folder, "r1")
    if master:
        PERSON_W6.append(os.path.join(master, "Bevel_Reducer.SLDASM"))


def section_r5(worker, excel):
    say("== r5  fixture B, Crossed_Slant (W6-PLAN §5.2): a crossed helical stage (skew, 90°), then a bevel stage at "
        "120° onto a slanted shaft, built fresh; §4.1 with the slanted axis on its line, the drive from the Right plane, "
        "both Flips with the interference judge on G1 meshes G2 and on G3 meshes G4, a quiet Update, reopen; then kept "
        "as r5.master")
    folder, path, book, desk = write_fixture(worker, excel, "r5", spec_crossed_slant, keep="Crossed_Slant.xlsx")
    expect_read(desk, "r5", B_EXPECT)
    pin_drive(desk, "r5", B_DRIVE)
    built_and_proved(worker, desk, "r5", 4, [("G1", "G2"), ("G3", "G4")])
    say_along(worker, desk, "r5 (G2's front face on the minus side of Right)")
    keep_master(worker, folder, "r5")


def section_r2(worker, excel):
    say("== r2  a copy of r1.master: the user's turn (37°) and Update with nothing changed; then S1 Z 60 -> 64 with G2 "
        "At 60 -> 64 (both cone tips up 4 mm together) by Update")
    folder, path, book, desk = start_copy(worker, excel, "r2", "r1", spec_bevel_reducer)
    user_turn(worker, desk, "r2", 37.0)
    save_assembly(worker, desk, "after the turn")
    desk.plan_solidworks()
    update_nothing_turned(worker, desk, "r2 turned 37°", folder)
    say("-- r2  Excel: S1 Z 60 -> 64, G2 At 60 -> 64")
    edit(desk, book, ("Shafts", "E2", 64), ("Gears", "C3", 64))
    u = desk.update
    desk.say_footer("r2, after the edit")
    if u is None or u.needs_new_revision or u.refusal:
        check(False, f"r2: the move is an Update: structural {u and list(u.structural)}; refusal {u and u.refusal!r}")
        end_copy(worker, folder, "r2")
        return
    check("S1" in u.moved_shafts and "G2" in u.replaced, f"classify: S1 moved and G2 re-placed: moved "
          f"{list(u.moved_shafts)}, re-place {list(u.replaced)}")
    pin_drive(desk, "r2", A_DRIVE)
    guard()
    _, result, _ = desk.update_solidworks()
    if result is None:
        check(False, f"r2: the Update refused: {desk.note[0]!r}")
        end_copy(worker, folder, "r2")
        return
    check(result.ok and sorted(result.placed) == all_mated(desk) and bool(result.restored) and result.ratios == [],
          f"r2: every gear put, the turned train restored, no gear mate remade: placed {result.placed}, restored "
          f"{result.restored}, ratios {result.ratios}")
    update_marks(worker, desk, result, "r2 moved", folder)
    box = desk.record.gearbox
    layout_values = run(worker, lambda s: live_globals(s, box.layout))
    assembly_values = run(worker, lambda s: live_globals(s, box.assembly))
    check(abs(float(layout_values.get("S1 Z", float("nan"))) - 64) < 1e-9, f"r2: the layout's \"S1 Z\" reads 64: "
          f"{layout_values}")
    check(abs(float(assembly_values.get("G2 Apex Z", float("nan"))) - 64) < 1e-9, f"r2: the assembly's \"G2 Apex Z\" "
          f"reads 64: {assembly_values}")
    live = measure_frames(worker, desk, "r2 moved")
    name_of = {c.gear: c.name for c in box.components}
    gap = max(abs(float(p) - float(q)) for p, q in zip(live[name_of["G1"]][1], live[name_of["G2"]][1]))
    check(gap <= FRAME_TOLERANCE, f"r2: the bevel cone tips together in SolidWorks: G1's and G2's origins {gap:.1e} mm "
          f"apart, at {tuple(round(float(v), 9) for v in live[name_of['G1']][1])}")
    measure_axes(worker, desk, "r2 moved")
    measure_mates(worker, desk, "r2 moved")
    measure_clear(worker, desk, "r2 moved")
    negative_controls(worker, desk, "r2 moved")
    drive_proof(worker, desk, "r2 moved")
    reopen(worker, desk, "r2 moved")
    end_copy(worker, folder, "r2")


def section_r3(worker, excel):
    say("== r3  a copy of r1.master: G1 Teeth 20 -> 21 (21 : 40 at 90°, still two cones) by Update: the turned gear mate "
        "G1 meshes G2 made again and read back (W6-INTERFACES §7.17 (a))")
    folder, path, book, desk = start_copy(worker, excel, "r3", "r1", spec_bevel_reducer)
    remake_update(worker, desk, book, "r3 G1 21", [("Gears", "F2", 21)], "G1 meshes G2", A_DRIVE_21, folder,
                  globals_wanted=[("G2", "Mate Teeth", 21.0), ("G1", "Mate Teeth", 40.0)])
    end_copy(worker, folder, "r3")


def section_r4(worker, excel):
    say("== r4  a copy of r1.master: S1 Axis X+ -> X- -> the structural sentence; Build again… makes Bevel_Reducer_r2 "
        "turning beside the earlier files; §4.1, the drive (the input measured about -X), both Flips on G1 meshes G2")
    folder, path, book, desk = start_copy(worker, excel, "r4", "r1", spec_bevel_reducer)
    edit(desk, book, ("Shafts", "F2", "X-"))
    u = desk.update
    said = " ".join(str(x) for x in (u.structural if u is not None else ()))
    check(u is not None and u.needs_new_revision and "S1's axis is now X- where it was built X+: the layout's axis "
          "and the mates on it keep the direction they were made with, so the gearbox needs building again." in said,
          f"classify: the structural sentence of §2.9: {said!r}")
    f = desk.say_footer("r4, after the edit")
    check(f.build_enabled, "r4: Build again… is offered")
    pin_drive(desk, "r4", A_DRIVE)
    earlier, sidecars = stamps(folder), sidecar_texts(folder)
    build_turning(worker, desk, "r4 Build again", None, None)
    box = desk.record.gearbox
    check(os.path.basename(box.assembly) == "Bevel_Reducer_r2.SLDASM" and box.revision == 2,
          f"r4: the new revision is Bevel_Reducer_r2: {os.path.basename(box.assembly)}, revision {box.revision}")
    check_earlier_unchanged(folder, earlier, "r4", sidecars)
    mate_readings(worker, desk, "r4 built")
    measure(worker, desk, "r4 built", controls=True, again=False)
    drive_proof(worker, desk, "r4 built, control on G1 meshes G2", control=("G1", "G2"))
    end_copy(worker, folder, "r4")


def section_r6(worker, excel):
    say("== r6  a copy of r5.master: G1 At 10 -> 11 by Update; G4 Teeth 30 -> 31 by Update (the 120° gear mate made "
        "again and read back); S3's direction changed (classify only); then the sense change of review M4 on the "
        "classify path, on fixture B's crossed stage alone")
    folder, path, book, desk = start_copy(worker, excel, "r6", "r5", spec_crossed_slant)
    say("-- r6  Excel: G1 At 10 -> 11 (\"G1 Face Z\" 2 -> 3; G2's phase follows G1's helix at the contact)")
    edit(desk, book, ("Gears", "C2", 11))
    u = desk.update
    if u is None or u.needs_new_revision or u.refusal:
        check(False, f"r6: G1 At is an Update: structural {u and list(u.structural)}; refusal {u and u.refusal!r}")
    else:
        pin_drive(desk, "r6 G1 At", B_DRIVE)
        guard()
        _, result, _ = desk.update_solidworks()
        if result is None:
            check(False, f"r6: the Update refused: {desk.note[0]!r}")
        else:
            check(result.ok and "G1" in result.axial and sorted(result.placed) == all_mated(desk)
                  and result.ratios == [], f"r6: \"G1 Face Z\" set and every gear put: axial {result.axial}, placed "
                  f"{result.placed}, ratios {result.ratios}")
            update_marks(worker, desk, result, "r6 G1 At", folder)
            values = run(worker, lambda s: live_globals(s, desk.record.gearbox.assembly))
            check(abs(float(values.get("G1 Face Z", float("nan"))) - 3) < 1e-9, f"r6: the assembly's \"G1 Face Z\" "
                  f"reads 3: {values}")
            measure_frames(worker, desk, "r6 G1 At")
            measure_mates(worker, desk, "r6 G1 At")
            measure_clear(worker, desk, "r6 G1 At")
            negative_controls(worker, desk, "r6 G1 At")
            drive_proof(worker, desk, "r6 G1 At")
            save_assembly(worker, desk, "after G1 At")
            desk.plan_solidworks()
    remake_update(worker, desk, book, "r6 G4 31", [("Gears", "F5", 31)], "G3 meshes G4", B_DRIVE_31, folder,
                  globals_wanted=[("G3", "Mate Teeth", 31.0), ("G4", "Mate Teeth", 20.0)])
    say("-- r6  Excel: S3's Axis -1, 1.732050807569, 0 -> -1, 1.8, 0 (classify only: nothing is built)")
    edit(desk, book, ("Shafts", "F4", "-1, 1.8, 0"))
    u = desk.update
    said = " ".join(str(x) for x in (u.structural if u is not None else ()))
    check(u is not None and u.needs_new_revision and "S3's axis slants, and the layout holds a slanted axis as a fixed "
          "line: its direction changed, so the gearbox needs building again." in said,
          f"classify: the slanted structural sentence of §2.9: {said!r}; gate {desk.a.lay_out_refusal()!r}")
    desk.say_footer("r6, S3's direction changed: nothing pressed")
    end_copy(worker, folder, "r6")
    sense_change(worker, excel)


def sense_change(worker, excel):
    """Review M4 on the classify path only (W6-PLAN §6.1 r6; the fake's round trip covers the worker): fixture B's
    crossed stage alone, off the Top plane, built to turn; then S1 moved to the other side of S2 in Excel: classify
    names G1 meshes G2 in ``resensed``, nothing structural, and the plan's remake carries the new sense (k −0.5 where
    the record holds +0.5). Nothing is pressed."""
    say("-- r6  the sense change of review M4: Crossed_Stage (fixture B's crossed stage, 10 mm up) built in r6-sense; "
        "S1 Y 10 -> 179.705628 (the other side of S2); classify only")
    folder, path, book, desk = write_fixture(worker, excel, "r6-sense", spec_crossed_stage)
    build_turning(worker, desk, "r6-sense", 2, None)
    mate_readings(worker, desk, "r6-sense built")
    edit(desk, book, ("Shafts", "D2", 179.705628))
    u = desk.update
    resensed = tuple(getattr(u, "resensed", ()) or ()) if u is not None else ()
    check(u is not None and not u.needs_new_revision and not u.refusal and resensed == ("G1 meshes G2",)
          and tuple(u.ratios) == () and tuple(u.moved_shafts) == ("S1",),
          f"classify: S1 moved, G1 meshes G2 to be made again for its sense alone: resensed {resensed}, ratios "
          f"{u and list(u.ratios)}, moved {u and list(u.moved_shafts)}, structural {u and list(u.structural)}, refusal "
          f"{u and u.refusal!r}")
    motion = u.motion if u is not None else None
    if motion is not None:
        now = [(m.a, m.b, m.k) for m in motion.meshes]
        then = [(m.a, m.b, m.k) for m in motion.recorded_meshes]
        say(f"fact    r6-sense: the plan's meshes {now}; the record's {then}; motion ratios {list(motion.ratios)}")
        check(now and then and now[0][:2] == ("G1", "G2") and abs(now[0][2] + then[0][2]) < 1e-12
              and abs(abs(now[0][2]) - 0.5) < 1e-12, "r6-sense: the plan's remake carries the new sense (k the "
              "record's, negated)")
    desk.say_footer("r6-sense, S1 on the other side: nothing pressed")
    end_copy(worker, folder, "r6-sense")


def section_r8(worker, excel):
    say("== r8  a copy of r5.master: the crossed stage's teeth G1 20 -> 21 and G2 40 -> 39 (the centre distance kept: "
        "2 · 60 / (2 cos 45°)) by Update: the skew gear mate G1 meshes G2 made again and read back (W6-INTERFACES "
        "§7.17 (a))")
    folder, path, book, desk = start_copy(worker, excel, "r8", "r5", spec_crossed_slant)
    remake_update(worker, desk, book, "r8 21 : 39", [("Gears", "F2", 21), ("Gears", "F3", 39)], "G1 meshes G2",
                  B_DRIVE_21_39, folder)
    end_copy(worker, folder, "r8")


def section_r7(worker, excel):
    say("== r7  fixture A on a Y input (Bevel_Reducer_Y): G1's cone tip at -30 along Y, an along mate to the Top plane "
        "with a negative coordinate; built fresh, frames against the plan, the drive from the Right plane, both Flips "
        "on G1 meshes G2 with the interference judge")
    folder, path, book, desk = write_fixture(worker, excel, "r7", spec_bevel_reducer_y)
    expect_read(desk, "r7", A_Y_EXPECT)
    pin_drive(desk, "r7", A_DRIVE)
    along = next((m for m in desk.plan.motion.mates if m.name == "G1 along S1"), None) if desk.plan else None
    check(along is not None and getattr(along, "plane", "") == "top" and along.z_front < 0,
          f"r7: G1's along mate is on the Top plane with a negative coordinate: "
          f"{along and (getattr(along, 'plane', ''), along.z_front, along.face_global)}")
    build_turning(worker, desk, "r7", 4, None)
    say_along(worker, desk, "r7")
    mate_readings(worker, desk, "r7 built")
    measure(worker, desk, "r7 built", controls=True, again=False)
    drive_proof(worker, desk, "r7 built, control on G1 meshes G2", control=("G1", "G2"))
    reopen(worker, desk, "r7 built")
    drive_proof(worker, desk, "r7 reopened")


# == W7: a planetary stage — carriers, copies, loops (W7-PLAN §4, §6) ==========================================
#
# Through the app's own code as W5's and W6's sections go, on the committed findings only. What only SolidWorks can
# show is measured here (W7-PLAN §6; the coordinator's list for W7): the app's own build of the 4 : 1 turning right
# — every body's turn and each copy's origin carried round the carrier under a temporary drive, interference on all
# six meshes (the two unmated ring meshes included) at the built position, at phases across a pitch and with the
# drive at 120, and both Flips on the ring mate and on a sun mate; every copy at its right angle (each turned half a
# pitch must clash with exactly its sun and its ring); the carrier part a skeleton of axes and planes, its axes
# carried into the assembly through each copy's centre; the puts of W7-INTERFACES §6.13 after a turn; the held
# sun, the stage on Z- and the held carrier; the carrier part's globals and every gear mate remade by Update;
# CarrierGear locked to the carrier; what SolidWorks does with a second planet–ring gear mate; quiet Updates.

PLANETARY = {"failed": ""}       # p1's build failing stops the sections that copy it (W7-PLAN §6)


def live_part(session, path):
    """A part's skeleton as SolidWorks holds it: its solid bodies, its top-level features (name, type), each axis's
    GetRefAxisParams by name, and its globals."""
    def work(s):
        doc = s._doc()  # noqa: SLF001
        found = call(doc, "GetBodies2", 0, True)
        solids = len(found) if found else 0
        tree, axes = [], {}
        feature = call(doc, "FirstFeature")
        while feature is not None:
            name, kind = str(call(feature, "Name")), str(call(feature, "GetTypeName2"))
            tree.append((name, kind))
            if kind == "RefAxis":
                axes[name] = [float(v) for v in call(call(feature, "GetSpecificFeature2"), "GetRefAxisParams")]
            feature = call(feature, "GetNextFeature")
        return solids, tree, axes, s.equation_values()
    return in_assembly(path, work)(session)


SOLID_FEATURES = ("Extrusion", "Boss", "Cut", "ICE", "Revolution", "Sweep", "Blend", "Fillet", "Chamfer")


def to_world(frame, point):
    """A point in a component's own coordinates carried into the assembly by its frame (rotation by rows, mm)."""
    rotation, at = frame
    return tuple(sum(float(rotation[i * 3 + j]) * float(point[j]) for j in range(3)) + float(at[i]) for i in range(3))


def carrier_part_check(worker, desk, label, live):
    """W7-PLAN §2.6, §6: each carrier part a skeleton — no solid body, no solid feature, only planes, axes and the
    sketch-free reference geometry — its globals the copies' offsets; and its axes, read in the part
    (GetRefAxisParams) and carried into the assembly by the carrier component's frame as SolidWorks holds it: the
    carrier's own axis on the carrier's line, each copy's axis through that copy's centre along the carrier's
    direction, to 1e-6 mm. Returns each carrier's globals."""
    box = desk.record.gearbox
    placed = desk.a.report.layout.placed
    out = {}
    for c in carriers_of(box):
        solids, tree, axes, values = run(worker, lambda s, p=c.path: live_part(s, p))
        made = [(n, t) for n, t in tree if t not in ("CommentsFolder", "FavoriteFolder", "HistoryFolder",
                                                      "SelectionSetFolder", "SensorFolder", "DocsFolder",
                                                      "DetailCabinet", "SurfaceBodyFolder", "SolidBodyFolder",
                                                      "EnvFolder", "InkMarkupFolder", "EqnFolder", "MaterialFolder",
                                                      "OriginProfileFeature")]
        say(f"        {os.path.basename(c.path)}: solid bodies {solids}; features {made}; globals {values}")
        check(solids == 0 and not any(any(k in t for k in SOLID_FEATURES) for _, t in made),
              f"{label}: {os.path.basename(c.path)} is axes and planes only: {solids} solid bodies, no solid feature")
        frame = live[c.component]
        direction = tuple(float(v) for v in c.direction)
        lines = {f"{c.shaft} Axis": (tuple(float(v) for v in frame[1]), "the carrier's own")}
        for axis in c.axes:
            copy = next((g for g, p in placed.items() if p.shaft == axis.shaft), None)
            if copy is not None:
                lines[axis.axis_name] = (tuple(placed[copy].centre), copy)
        for name, (point, what) in lines.items():
            params = axes.get(name)
            if params is None:
                check(False, f"{label}: {os.path.basename(c.path)} holds the axis {name}")
                continue
            world = [to_world(frame, [v * 1000.0 for v in params[:3]]),
                     to_world(frame, [v * 1000.0 for v in params[3:6]])]
            off, u, dot = axis_on_line([v / 1000.0 for v in world[0] + world[1]], point, direction)
            check(off <= 1e-6 and abs(abs(dot) - 1.0) <= 1e-9,
                  f"{label}: {name}, carried into the assembly, through {what} centre {tuple(round(v, 9) for v in point)} "
                  f"(off {off:.1e} mm) along the carrier's direction ({'+' if dot > 0 else '-'})")
        out[c.shaft] = values
    return out


def held_fixed(worker, desk, label):
    """Every held body (``box.fixed``: the held member, a held carrier and what is held with it) reads IsFixed True;
    no mate names a held carrier (W7-PLAN §2.7: inserted, placed and fixed, never mated)."""
    box = desk.record.gearbox
    pairs = [(g, n) for g, n in bodies(box) if g in box.fixed]

    def work(s):
        out = {}
        for index, (g, n) in enumerate(pairs):
            s.find_component(f"h{index}", n)
            out[g] = s.is_fixed(f"h{index}")
        return out
    got = run(worker, in_assembly(box.assembly, work)) if pairs else {}
    check(all(got.values()), f"{label}: every held body reads IsFixed: {got}")
    held_carriers = [wb_layout.carrier_id(c.shaft) for c in carriers_of(box)
                     if wb_layout.carrier_id(c.shaft) in box.fixed]
    if held_carriers:
        named = [m.name for m in box.mates if any(h in m.gears for h in held_carriers)]
        check(not named, f"{label}: no mate names the held carrier {held_carriers}: {named}")


def copy_controls(worker, desk, label):
    """Every copy built at its right angle (W7-PLAN §6; the coordinator's (2)): each copy turned half its pitch about
    its own axis (a put with its gear mates on, MESH_PHASE_ROUTE) must clash with exactly its sun and its ring, and
    nothing else; the sun turned half its pitch with every copy and nothing else; put back, none again."""
    box = desk.record.gearbox
    placed = desk.a.report.layout.placed
    name_of = {g: n for g, n in bodies(box)}
    gear_of = {n: g for g, n in bodies(box)}
    want = wanted(desk)
    meshes = wb_geometry.expand_meshes(desk.a.spec, placed)
    turned_gears = [g for g in placed if getattr(placed[g], "carrier", "")]
    stage = desk.a.report.stages[0]
    if stage.sun not in box.fixed:
        turned_gears.append(stage.sun)
    for gear in turned_gears:
        partners = {b if a == gear else a for a, b in meshes if gear in (a, b)}
        rotation, at, pitch = want[gear]
        started = time.monotonic()
        try:
            moved, back = run(worker, lambda s: placed_elsewhere(s, box.assembly, name_of[gear],
                                                                  turn_about_z(rotation, pitch / 2), at,
                                                                  swcom.ASSEMBLY_TRAIN))
        except Exception as exc:  # noqa: BLE001 - a put that does not hold is a finding, said
            check(False, f"{label}: {gear} turned half a pitch: the put raised {type(exc).__name__}: {exc}")
            continue
        merged = swbuild._clashes(moved, gear_of)  # noqa: SLF001
        pairs = {frozenset(c.gears) for c in merged if c.volume > 0}
        check(pairs == {frozenset((gear, p)) for p in partners},
              f"{label}: {gear} turned half a pitch ({pitch / 2:.4f}°) clashes with exactly {sorted(partners)}: "
              f"{[(c.gears, round(c.volume, 3)) for c in merged]}")
        check(back == [], f"{label}: {gear} put back, no interference ({time.monotonic() - started:.1f} s)")
    measure_frames(worker, desk, f"{label}, after the controls")
    measure_mates(worker, desk, f"{label}, after the controls")


def second_ring_mate(worker, desk, label):
    """The coordinator's (8): what SolidWorks really does with a second planet–ring gear mate (the fake calls it
    over-defined; no probe has seen it). On a copy, at the end of its section, never saved: ``Planet copy 2`` gear-
    mated to the ring at the tooth ratio with each Flip in turn; AddMate5's status, every mate's code and warning,
    every body's constrained status and the rebuild's answer logged as facts; deleted; the mates read again equal to
    the record's, nothing suppressed, codes 0."""
    box = desk.record.gearbox
    pairs = bodies(box)
    teeth = {g: desk.a.report.layout.placed[g].teeth for g, _ in pairs if g in desk.a.report.layout.placed}
    a, b = "Planet copy 2", desk.a.report.stages[0].ring

    def job(session):
        out = {}
        session.begin_build()
        try:
            session.open_document(box.assembly)
            handle = {}
            for index, (g, n) in enumerate(pairs):
                session.find_component(f"x{index}", n)
                handle[g] = f"x{index}"
            out["before"] = [(s.name, s.code, s.warning, s.suppressed) for s in session.mate_states()]
            for flip in (bool(findings.GEAR_MATE_FLIP), not bool(findings.GEAR_MATE_FLIP)):
                try:
                    name, _ = session.add_mate("x2nd", "gear", f"{handle[a]}:Gear Axis", f"{handle[b]}:Gear Axis",
                                               0.0, f"{CONTROL}{a} meshes {b}", ratio=(float(teeth[a]), float(teeth[b])),
                                               flip=flip)
                    out[f"status {flip}"] = session.mate_status(name)
                    out[f"rebuild {flip}"] = bool(session.rebuild(kind=swcom.ASSEMBLY_TRAIN))
                    out[f"states {flip}"] = [(s.name, s.code, s.warning, s.suppressed) for s in session.mate_states()]
                    out[f"constrained {flip}"] = {g: session.constrained_status(h) for g, h in handle.items()}
                    delete_mate(session, name)
                    session.rebuild(kind=swcom.ASSEMBLY_TRAIN)
                except Exception as exc:  # noqa: BLE001 - what SolidWorks answered is the finding
                    out[f"raised {flip}"] = f"{type(exc).__name__}: {exc}"
            out["after"] = [(s.name, s.code, s.warning, s.suppressed) for s in session.mate_states()]
            return out
        finally:
            session.end_build()
    say(f"control {label}: a second planet–ring gear mate, {a} meshes {b} at {teeth.get(a)} : {teeth.get(b)}, made with "
        "each Flip on this copy and deleted; never saved")
    out = run(worker, job)
    for flip in (bool(findings.GEAR_MATE_FLIP), not bool(findings.GEAR_MATE_FLIP)):
        say(f"fact    {label}: the second ring mate with Flip {flip}: AddMate5 status {out.get(f'status {flip}')}, "
            f"rebuild {out.get(f'rebuild {flip}')}, raised {out.get(f'raised {flip}')!r}")
        say(f"fact    {label}:   mates then {out.get(f'states {flip}')}")
        say(f"fact    {label}:   constrained then {out.get(f'constrained {flip}')}")
    check(out.get("after") == out.get("before"), f"{label}: the second ring mate deleted, the mates as before: "
          f"{out.get('after')}")


def spec_planetary(folder=""):
    """W7-PLAN §4.1, ``Planetary_4to1``: the ring held, the sun in at 1000 rpm and 2 N·m, the carrier out, three
    planets on P (mounted on C), CarrierGear on C locked to the carrier (as tests/test_workbook_planetary.py has it)."""
    return GearboxSpec(
        box=Box(name="Planetary_4to1", output_folder=folder, pressure_angle="20", efficiency="98"),
        shafts=(Shaft("S", "frame", "0", "0", "0", "Z+", "input", "", "1000", "2"),
                Shaft("C", "frame", "0", "0", "0", "Z+", "output"),
                Shaft("P", "C", "18", "0", "0", "", "", "3"),
                Shaft("R", "frame", "0", "0", "0", "Z+", "fixed")),
        gears=(Gear("Sun", "S", "10", "spur", "external", "18", "1", "", "10", "6", part_name="Sun"),
               Gear("Planet", "P", "10", "spur", "external", "18", "1", "", "10", "8", part_name="Planet"),
               Gear("Ring", "R", "10", "spur", "internal", "54", "1", "", "10", ""),
               Gear("CarrierGear", "C", "30", "spur", "external", "20", "1", "", "6", "10", part_name="CarrierGear")),
        meshes=(Mesh("Sun", "Planet"), Mesh("Planet", "Ring")))


COPIES3 = ("Planet copy 1", "Planet copy 2", "Planet copy 3")
P_EXPECT = {
    "header": "Planetary, R fixed · 3 planets · 4.000 : 1 · output turns the same way",
    "speeds": {"S": 1000.0, "C": 250.0, "P": -500.0, "R": 0.0}, "relative": {"P": -750.0},
    "torques": {"S": 2.0, "C": 7.7624}, "held": {"R": 5.7624},
    "lines": ["S     1000.0 rpm anticlockwise · 2.00 N·m", "C     250.0 rpm anticlockwise · 7.76 N·m",
              "P     500.0 rpm clockwise, 750.0 rpm clockwise relative to C · 3 copies", "R     held still · 5.76 N·m"]}
P5_EXPECT = {
    "header": "Planetary, S fixed · 3 planets · 1.333 : 1 · output turns the same way",
    "speeds": {"S": 0.0, "C": 750.0, "P": 1500.0, "R": 1000.0}, "relative": {"P": 750.0},
    "torques": {"R": 2.0, "C": 2.6403}, "held": {"S": 0.6403},
    "lines": ["S     held still · 0.64 N·m", "C     750.0 rpm anticlockwise · 2.64 N·m",
              "P     1500.0 rpm anticlockwise, 750.0 rpm anticlockwise relative to C · 3 copies",
              "R     1000.0 rpm anticlockwise · 2.00 N·m"]}
P7_EXPECT = {
    "header": "Planetary, C fixed · 3 planets · 3.000 : 1 · output turns the other way",
    "speeds": {"S": 1000.0, "C": 0.0, "P": -1000.0, "R": -1000.0 / 3}, "relative": {"P": -1000.0},
    "torques": {"S": 2.0, "R": 5.7624}, "held": {"C": 7.7624},
    "lines": ["S     1000.0 rpm anticlockwise · 2.00 N·m", "C     held still · 7.76 N·m",
              "P     1000.0 rpm clockwise, 1000.0 rpm clockwise relative to C · 3 copies",
              "R     333.3 rpm clockwise · 5.76 N·m"]}
# Each body's own turn for +30° of the input (W7-PLAN §4, §6 p3), worked by hand there.
P_DRIVE = dict({"Sun": 30.0, "C carrier": 7.5, "CarrierGear": 7.5, "Ring": 0.0}, **{c: -15.0 for c in COPIES3})
P3_DRIVE = dict({"Sun": 30.0, "C carrier": 30.0 * 21 / 78, "CarrierGear": 30.0 * 21 / 78, "Ring": 0.0},
                **{c: -17.5 for c in COPIES3})                       # Sun 21, Ring 57, P X 19.5: 3.714 : 1
P5_DRIVE = dict({"Ring": 30.0, "C carrier": 22.5, "CarrierGear": 22.5, "Sun": 0.0}, **{c: 45.0 for c in COPIES3})
P7_DRIVE = dict({"Sun": 30.0, "C carrier": 0.0, "CarrierGear": 0.0, "Ring": -10.0}, **{c: -30.0 for c in COPIES3})
P_CARRIER_GLOBALS = {"P copy 1 X": 18.0, "P copy 2 X": -9.0, "P copy 2 Y": 15.588457268, "P copy 3 X": -9.0,
                     "P copy 3 Y": -15.588457268}
P3_CARRIER_GLOBALS = {"P copy 1 X": 19.5, "P copy 2 X": -9.75, "P copy 2 Y": 16.887495374, "P copy 3 X": -9.75,
                      "P copy 3 Y": -16.887495374}


def expect_planetary_read(desk, label, expect):
    """The read against W7-PLAN §4: no diagnostic at all (B's tests: the fixtures check clean), the header, each
    shaft's own-axis speed, the planet's speed on its carrier, the torques and the held member's, the Speeds lines
    (D's tests' wording, no-break spaces read as spaces), the stage recognised."""
    a = desk.a
    said = [d.message for d in a.diagnostics]
    check(not said and a.lay_out_refusal() == "", f"{label}: the Checks panel is empty and the gate open: {said}; "
          f"gate {a.lay_out_refusal()!r}")
    check(a.report.worked_out_as == expect["header"], f"{label}: the header {a.report.worked_out_as!r}")
    m = a.report.motion
    close = lambda got, want: got is not None and abs(float(got) - want) <= 1e-9 * max(1.0, abs(want))  # noqa: E731
    check(all(close(m.speeds.get(k), v) for k, v in expect["speeds"].items()),
          f"{label}: own-axis speeds §4's: {({k: float(v) for k, v in m.speeds.items()})}")
    relative = dict(getattr(m, "relative", {}) or {})
    check(all(close(relative.get(k), v) for k, v in expect["relative"].items()),
          f"{label}: the planet's speed on its carrier: {({k: float(v) for k, v in relative.items()})}")
    torques = {k: float(v) for k, v in m.torques.items()}
    held = {k: float(v) for k, v in (getattr(m, "held", {}) or {}).items()}
    check(all(k in torques and abs(torques[k] - v) <= 1e-4 for k, v in expect["torques"].items())
          and all(k in held and abs(held[k] - v) <= 1e-4 for k, v in expect["held"].items()),
          f"{label}: torques {torques}, held {held}")
    lines, readout = ui_text.workbook_speed_lines(a.spec, m)
    for line in lines:
        say(f"speeds  {line}")
    plain = [line.replace("\u00a0", " ") for line in lines]
    check(plain == expect["lines"], f"{label}: the Speeds lines are D's tests' (no-break spaces as spaces)")
    stages = getattr(a.report, "stages", ())
    say(f"        stage {stages}")
    check(len(stages) == 1, f"{label}: one planetary stage recognised")


def planetary_built(worker, desk, label, parts, controls, phases=True):
    """A planetary built (fresh or Build again…) and judged: built to turn, which Flip each gear mate kept logged;
    the mates exactly the plan's (one per sun mesh, one with the ring: W7-INTERFACES §6.14), the unmated ring meshes
    on record; every gear mate's read; §4.1 with the carrier part, the held members and the copies' controls; the
    drive with the both-Flips control and the interference judge on each mesh in ``controls`` (phases across the
    input's pitch on the first, the interference read there too); a quiet Update; reopened, read, driven again."""
    build_turning(worker, desk, label, parts, None)
    box = desk.record.gearbox
    gear_mates = [m.name for m in box.mates if m.kind == "mesh"]
    say(f"fact    {label}: gear mates {gear_mates}; unmated {box.unmated}; fixed {box.fixed}; drag {box.drag}; "
        f"carriers {[(c.shaft, c.component, os.path.basename(c.path)) for c in carriers_of(box)]}")
    stage = desk.a.report.stages[0]
    copies = [g for g, p in desk.a.report.layout.placed.items() if getattr(p, "carrier", "")]
    check(sorted(gear_mates) == sorted([f"{stage.sun} meshes {c}" for c in copies] + [f"{copies[0]} meshes {stage.ring}"]),
          f"{label}: one gear mate per sun mesh and exactly one with the ring, with copy 1: {gear_mates}")
    check(sorted(map(tuple, box.unmated)) == sorted((c, stage.ring) for c in copies[1:]),
          f"{label}: the other ring meshes left unmated on record: {box.unmated}")
    mate_readings(worker, desk, f"{label} built")
    measure(worker, desk, f"{label} built", controls=True, again=False)
    input_gear = box.drag[0] if box.drag else ""
    pitch = wb_layout.pitch(desk.a.report.layout.placed[input_gear]) if input_gear else 0.0
    for index, control in enumerate(controls):
        drive_proof(worker, desk, f"{label} built, control on {control[0]} meshes {control[1]}", control=control,
                    phases=(pitch / 4, pitch / 2, 3 * pitch / 4) if phases and index == 0 else ())
    quiet_update(worker, desk, f"{label} quiet Update")
    reopen(worker, desk, f"{label} built")
    mate_readings(worker, desk, f"{label} reopened")
    drive_proof(worker, desk, f"{label} reopened, control on {controls[0][0]} meshes {controls[0][1]}",
                control=controls[0])


def p_blocked(section):
    if PLANETARY["failed"]:
        check(False, f"{section}: not run: p1's build of Planetary_4to1 failed ({PLANETARY['failed']}), and every "
                     "later planetary section starts from it")
        return True
    return False


def section_p1(worker, excel):
    say("== p1  Planetary_4to1 (W7-PLAN §4.1): the ring held, three planets on C, CarrierGear locked to the carrier; "
        "built fresh; every-build checks, the drive with both Flips on Planet copy 1 meshes Ring and on Sun meshes "
        "Planet copy 2, phases across the sun's pitch, a quiet Update, reopen; then kept as p1.master")
    folder, path, book, desk = write_fixture(worker, excel, "p1", spec_planetary, keep="Planetary_4to1.xlsx")
    expect_planetary_read(desk, "p1", P_EXPECT)
    pin_drive(desk, "p1", P_DRIVE, input_gear="Sun")
    try:
        planetary_built(worker, desk, "p1", 4, [("Planet copy 1", "Ring"), ("Sun", "Planet copy 2")])
    except (Halt, Stopped):
        raise
    except Exception as exc:
        PLANETARY["failed"] = f"{type(exc).__name__}: {exc}"
        raise
    master = keep_master(worker, folder, "p1")
    if master:
        PERSON_W7.append(os.path.join(master, "Planetary_4to1.SLDASM"))


def turned_then(worker, desk, label):
    """W7-PLAN §6 p3 (review M5): the train driven 37° and the drive deleted, saved, so the carrier stands at
    δ_c = 9.25° before the edit."""
    user_turn(worker, desk, label, 37.0)
    save_assembly(worker, desk, f"{label}: after the turn")
    desk.plan_solidworks()


def section_p2(worker, excel):
    say("== p2  a copy of p1.master: the user's turn (37°) and Update with nothing changed; then, at the end, on this "
        "copy and never saved, a second planet–ring gear mate")
    if p_blocked("p2"):
        return
    folder, path, book, desk = start_copy(worker, excel, "p2", "p1", spec_planetary)
    turned_then(worker, desk, "p2")
    update_nothing_turned(worker, desk, "p2 turned 37°", folder)
    second_ring_mate(worker, desk, "p2")
    end_copy(worker, folder, "p2", save=False)


def put_order(result, label, first):
    """The order the Update put things in (``GearboxUpdate.placed``), against W7-INTERFACES §6.13: ``first`` the
    bodies that must come first, in that order."""
    say(f"fact    {label}: put in the order {result.placed}")
    check(list(result.placed[:len(first)]) == list(first), f"{label}: put first {list(first)}: {result.placed}")


def section_p3(worker, excel):
    say("== p3  a copy of p1.master: puts, moves and values on a turned carrier — before each edit the train driven "
        "37° and the drive deleted: (1) Planet At 10 -> 12; (2) Ring At 10 -> 12, the held ring put first; (3) Sun 21, "
        "Ring 57, P's X 19.5: the carrier part's globals and all four gear mates remade, 3.714 : 1")
    if p_blocked("p3"):
        return
    folder, path, book, desk = start_copy(worker, excel, "p3", "p1", spec_planetary)
    carrier = wb_layout.carrier_id("C")
    for step, cells, first, why in (
            ("(1)", [("Gears", "C3", 12)], [carrier], "Planet At 10 -> 12: \"Planet Face Z\" set once"),
            ("(2)", [("Gears", "C4", 12)], ["Ring", carrier], "Ring At 10 -> 12: the gear-mated held ring")):
        if step.strip("()") not in P3_STEPS:
            continue
        label = f"p3 {step}"
        say(f"-- {label}  {why}")
        turned_then(worker, desk, label)
        edit(desk, book, *cells)
        u = desk.update
        if u is None or u.needs_new_revision or u.refusal:
            check(False, f"{label}: an Update: structural {u and list(u.structural)}; refusal {u and u.refusal!r}")
            continue
        guard()
        _, result, _ = desk.update_solidworks()
        if result is None:
            check(False, f"{label}: the Update refused: {desk.note[0]!r}")
            continue
        say(f"fact    {label}: axial {result.axial}; restored {result.restored}; unsuppressed {result.unsuppressed}")
        for line in result.log_lines():
            if "lock" in line.lower() or "suppress" in line.lower() or " put" in line.lower():
                say(f"fact    {label}: log: {line.strip()}")
        check(result.ok and bool(result.restored), f"{label}: the turned train put back: restored {result.restored}")
        put_order(result, label, first)
        update_marks(worker, desk, result, label, folder)
        measure_frames(worker, desk, label)
        measure_mates(worker, desk, label)
        measure_clear(worker, desk, label)
        drive_proof(worker, desk, f"{label}, driven after")
        save_assembly(worker, desk, f"{label}: after the drive")
        desk.plan_solidworks()
    if "3" in P3_STEPS:
        label = "p3 (3)"
        say(f"-- {label}  Sun 18 -> 21, Ring 54 -> 57, P's X 18 -> 19.5 (centres 19.5 / 19.5, (21 + 57)/3 = 26)")
        turned_then(worker, desk, label)
        remake_planetary(worker, desk, book, label, folder)
    end_copy(worker, folder, "p3")


def remake_planetary(worker, desk, book, label, folder):
    """p3's third edit (W7-PLAN §6 p3 (3); the coordinator's (6)): two parts' values, the carrier part's globals,
    all four gear mates remade (copy 1's planet carries two) and read back, the swing put right; frames, the carrier
    part, interference and the controls; the drive at 3.714 : 1 with both Flips on the ring mate; a quiet Update;
    reopen; drive."""
    edit(desk, book, ("Gears", "F2", 21), ("Gears", "F4", 57), ("Shafts", "C4", 19.5))
    u = desk.update
    desk.say_footer(f"{label}, after the edit")
    if u is None or u.needs_new_revision or u.refusal:
        check(False, f"{label}: an Update: structural {u and list(u.structural)}; refusal {u and u.refusal!r}")
        return
    mates = sorted(m.name for m in desk.record.gearbox.mates if m.kind == "mesh")
    check(sorted(u.ratios) == mates, f"classify: every gear mate remade: ratios {list(u.ratios)}; carriers moved "
          f"{list(getattr(u, 'carriers_moved', ()))}")
    pin_drive(desk, label, P3_DRIVE, input_gear="Sun")
    guard()
    _, result, _ = desk.update_solidworks()
    if result is None:
        check(False, f"{label}: the Update refused: {desk.note[0]!r}")
        return
    say(f"fact    {label}: ratios {result.ratios}, read {result.ratios_read}, turned round "
        f"{getattr(result, 'turned_round', None)}, sense found wrong {getattr(result, 'sense_found_wrong', None)}, "
        f"carriers {[(r.document, r.changed) for r in getattr(result, 'carriers', [])]}, placed {result.placed}")
    check(result.ok and sorted(result.ratios) == mates, f"{label}: all four gear mates remade: {result.ratios}")
    update_marks(worker, desk, result, label, folder)
    live = measure_frames(worker, desk, label)
    values = carrier_part_check(worker, desk, label, live).get("C", {})
    check(all(abs(abs(float(values.get(k, float("nan")))) - abs(v)) < 1e-6 for k, v in P3_CARRIER_GLOBALS.items()),
          f"{label}: the carrier part's globals put the copies at (19.5, 0), (-9.75, ±16.887495374): {values}")
    mate_readings(worker, desk, f"{label}, remade")
    measure_mates(worker, desk, label)
    measure_clear(worker, desk, label)
    copy_controls(worker, desk, label)
    drive_proof(worker, desk, f"{label}, at 3.714 : 1", control=("Planet copy 1", "Ring"))
    quiet_update(worker, desk, f"{label}, quiet Update")
    reopen(worker, desk, label)
    mate_readings(worker, desk, f"{label}, reopened")
    drive_proof(worker, desk, f"{label}, reopened, at 3.714 : 1")


def build_again(worker, desk, label, folder, sentence):
    """A structural edit's Build again… (W7-PLAN §6 p4–p7): the classify sentence, then ``_r2`` built turning beside
    the earlier files, whose sha256 and mtime stay as they were."""
    u = desk.update
    said = " ".join(str(x) for x in (u.structural if u is not None else ()))
    check(u is not None and u.needs_new_revision and (sentence in said if sentence else True),
          f"{label}: structural: {said!r}")
    f = desk.say_footer(f"{label}, after the edit")
    check(f.build_enabled, f"{label}: Build again… offered")
    earlier, sidecars = stamps(folder), sidecar_texts(folder)
    build_turning(worker, desk, f"{label} Build again", None, None)
    box = desk.record.gearbox
    check(box.revision == 2 and os.path.basename(box.assembly) == "Planetary_4to1_r2.SLDASM",
          f"{label}: the new revision is Planetary_4to1_r2: {os.path.basename(box.assembly)}")
    check_earlier_unchanged(folder, earlier, label, sidecars)


def section_p4(worker, excel):
    say("== p4  a copy of p1.master: Copies 5 (the assembly condition), Copies 6 (the neighbours), then Copies 4 -> "
        "Build again… with four copies of the one Planet part")
    if p_blocked("p4"):
        return
    folder, path, book, desk = start_copy(worker, excel, "p4", "p1", spec_planetary)
    for copies, wanted_text in ((5, "5 copies of Planet cannot all mesh with Sun and Ring at once"),
                                (6, "6 copies of Planet stand")):
        edit(desk, book, ("Shafts", "H4", copies))
        errors = [d.message for d in desk.a.diagnostics if d.level == "error"]
        f = desk.say_footer(f"p4, Copies {copies}")
        check(any(wanted_text in m for m in errors) and not f.build_enabled and not f.update_enabled,
              f"p4: Copies {copies} is an error, Build and Update not offered: {errors}")
    edit(desk, book, ("Shafts", "H4", 4))
    build_again(worker, desk, "p4", folder, "P now has 4 copies where it was built with 3")
    box = desk.record.gearbox
    copies = [c for c in box.components if getattr(c, "of", "") == "Planet"]
    check(len(copies) == 4 and len({c.part for c in copies}) == 1, f"p4: four copies of the one Planet part: "
          f"{[(c.gear, c.name, os.path.basename(c.part)) for c in copies]}")
    mate_readings(worker, desk, "p4 built")
    measure(worker, desk, "p4 built", controls=True, again=False)
    drive_proof(worker, desk, "p4 built, control on Planet copy 1 meshes Ring", control=("Planet copy 1", "Ring"))
    end_copy(worker, folder, "p4")


def held_variant(worker, excel, section, cells, expect, drive_pin, sentence, input_gear, control):
    """p5–p7: a copy of p1.master, the Role or Axis edits, the structural sentence, Build again… ``_r2``; then as p1:
    every-build checks, the drive (with both Flips on ``control``), reopen, the drive again."""
    if p_blocked(section):
        return None
    folder, path, book, desk = start_copy(worker, excel, section, "p1", spec_planetary)
    edit(desk, book, *cells)
    expect_planetary_read(desk, section, expect) if expect else None
    pin_drive(desk, section, drive_pin, input_gear=input_gear)
    build_again(worker, desk, section, folder, sentence)
    box = desk.record.gearbox
    check(box.drag and box.drag[0] == input_gear, f"{section}: the gear to drag is {input_gear}: {box.drag}")
    mate_readings(worker, desk, f"{section} built")
    measure(worker, desk, f"{section} built", controls=True, again=False)
    drive_proof(worker, desk, f"{section} built, control on {control[0]} meshes {control[1]}", control=control)
    reopen(worker, desk, f"{section} built")
    mate_readings(worker, desk, f"{section} reopened")
    drive_proof(worker, desk, f"{section} reopened")
    return folder, desk


def section_p5(worker, excel):
    say("== p5  a copy of p1.master: the sun held (S fixed, R the input) -> Build again…; the drive from the ring")
    done = held_variant(worker, excel, "p5", [("Shafts", "G2", "fixed"), ("Shafts", "I2", None), ("Shafts", "J2", None),
                                              ("Shafts", "G5", "input"), ("Shafts", "I5", 1000), ("Shafts", "J5", 2)],
                        P5_EXPECT, P5_DRIVE, "", "Ring", ("Planet copy 1", "Ring"))
    if done:
        end_copy(worker, done[0], "p5")


def section_p6(worker, excel):
    say("== p6  a copy of p1.master: S, C and R on Z- -> Build again…; the copies where §4.3 puts them, the carrier "
        "part's own coordinates p1's; the input's turn measured")
    done = held_variant(worker, excel, "p6", [("Shafts", "F2", "Z-"), ("Shafts", "F3", "Z-"), ("Shafts", "F5", "Z-")],
                        None, P_DRIVE, "", "Sun", ("Planet copy 1", "Ring"))
    if done:
        folder, desk = done
        live = gear_frames(worker, desk)
        values = carrier_part_check(worker, desk, "p6", {c.component: live[wb_layout.carrier_id(c.shaft)]
                                                         for c in carriers_of(desk.record.gearbox)}).get("C", {})
        check(all(abs(float(values.get(k, float("nan"))) - v) < 1e-6 for k, v in P_CARRIER_GLOBALS.items()),
              f"p6: the carrier part holds p1's own coordinates: {values}")
        end_copy(worker, folder, "p6")


def section_p7(worker, excel):
    say("== p7  a copy of p1.master: the carrier held (C fixed, R the output) -> Build again…; the carrier and "
        "CarrierGear fixed and never mated; copies -30°, Ring -10° for +30° on the sun")
    done = held_variant(worker, excel, "p7", [("Shafts", "G3", "fixed"), ("Shafts", "G5", "output")],
                        P7_EXPECT, P7_DRIVE, "", "Sun", ("Planet copy 1", "Ring"))
    if done:
        end_copy(worker, done[0], "p7")


# -- W8: sleeves and modes (W8-PLAN §5) -------------------------------------------------------------------------
#
# Every SolidWorks job below opens the assembly (which raises the session's configuration epoch), shows the mode it
# works in and rebuilds the train before it finds any component, so no handle is ever held across a configuration
# change (W8-PLAN §1.8's handle rule; W8-SPIKE.md: the spike's first three runs stopped on exactly that). Components
# are found by the Name2 the record holds, mates by the record's names; selections go through swcom, by full names.


W8_MASTER = {"failed": ""}       # s1's build failing stops the sections that copy s1.master (W8-PLAN §5, J24)
STOPS = []                       # W8-PLAN §0.5's STOP triggers seen: each a FAIL, listed again at the end


def stop_check(ok, what):
    """A check whose failure is one of W8-PLAN §0.5's STOP triggers: a FAIL, and listed for the coordinator to rule
    on before anything is built on it. The section goes on, so the log holds the rest of what SolidWorks did."""
    if not check(ok, what):
        STOPS.append(what)
        say("STOP    W8-PLAN §0.5: the above is a STOP trigger; the run goes on gathering, nothing is built on it")
    return ok


def frame_none_stop(texts, label):
    """W8-PLAN §0.5 (review S5): a frame reading None — SolidWorks' answer through a handle held across a configuration
    change, which ``component_frame`` refuses with "gave no frame" — is a STOP, not a retry."""
    for text in texts:
        if "gave no frame" in str(text):
            STOPS.append(f"{label}: a frame read None: {text}")
            say(f"STOP    W8-PLAN §0.5: {label}: a frame read None (a handle held across a configuration change?)")
            return True
    return False


def w8_fixtures():
    """``tests/workbook_fixtures.py``, the one home of W8's two fixtures (W8-PLAN §2), loaded from the snapshot."""
    import importlib.util
    path = os.path.join(REPO, "tests", "workbook_fixtures.py")
    spec = importlib.util.spec_from_file_location("workbook_fixtures", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def spec_parallel(folder=""):
    """W8-PLAN §2.2, ``TransferCase_Parallel``: the low range on a reverted layshaft, every shaft a frame shaft."""
    made = w8_fixtures().transfer_case_parallel()
    return dataclasses.replace(made, box=dataclasses.replace(made.box, output_folder=folder))


def spec_e4(folder=""):
    """W8-PLAN §2.1, the E4 transfer case (``TransferCase_E4``): E3's 4 : 1 planetary as the low range."""
    made = w8_fixtures().e4_transfer_case()
    return dataclasses.replace(made, box=dataclasses.replace(made.box, output_folder=folder))


# W8-PLAN §2.3, the answer key, worked by hand there (both fixtures alike but for the low range).
W8_MODES = ("2H", "4H", "N", "4L")
W8_ENGAGED = {"2H": (("RangeSlv", "InDog"),), "4H": (("RangeSlv", "InDog"), ("ModeSlv", "FrontDog")), "N": (),
              "4L": (("RangeSlv", "LoDog"), ("ModeSlv", "FrontDog"))}
W8_POSITIONS = {"2H": {"RangeSlv": ("H", -10.0), "ModeSlv": ("2WD", 0.0)},
                "4H": {"RangeSlv": ("H", -10.0), "ModeSlv": ("4WD", 10.0)},
                "N": {"RangeSlv": ("N", 0.0), "ModeSlv": ("2WD", 0.0)},
                "4L": {"RangeSlv": ("L", 10.0), "ModeSlv": ("4WD", 10.0)}}
W8_SLIDES = {"RangeSlv along Rear": {"2H": 46.0, "4H": 46.0, "N": 56.0, "4L": 66.0},
             "ModeSlv along Rear": {"2H": 96.0, "4H": 106.0, "N": 96.0, "4L": 106.0}}
W8_COUPLES = {"RangeSlv engages InDog": ("2H", "4H"), "RangeSlv engages LoDog": ("4L",),
              "ModeSlv engages FrontDog": ("4H", "4L")}
W8_ALWAYS = {"RangeSlv on Rear Axis": "axis", "ModeSlv on Rear Axis": "axis", "ModeSlv splined to RangeSlv": "spline"}
W8_SPLINE = ("RangeSlv", "ModeSlv")
# §2.3's 30° row, by shaft, about each shaft's own +Z (the speeds are 50 times these, in rpm); None: free in that
# mode (no speed: the shaft must not turn, and one that does is a NOTE).
W8_REAR_FRONT = {"2H": {"Rear": 30.0, "FrontDrv": None, "Idler": None, "Front": None},
                 "4H": {"Rear": 30.0, "FrontDrv": 30.0, "Idler": -45.0, "Front": 30.0},
                 "N": {"Rear": None, "FrontDrv": None, "Idler": None, "Front": None},
                 "4L": {"Rear": 7.5, "FrontDrv": 7.5, "Idler": -11.25, "Front": 7.5}}
W8_LOW = {"TransferCase_Parallel": {"In": 30.0, "Lay": -15.0, "Lo": 7.5},
          "TransferCase_E4": {"In": 30.0, "Carrier": 7.5, "Planet": -15.0, "Ring": 0.0}}
W8_RATIOS = {"2H": 1.0, "4H": 1.0, "N": None, "4L": 4.0}
# The both-Flips controls (W8-PLAN §5, review M6): (mode, the recorded gear mate, the gear its Flip decides).
W8_FLIP_CONTROLS = (("4H", "ModeSlv splined to RangeSlv", "ModeSlv"), ("4L", "RangeSlv engages LoDog", "RangeSlv"))


# The key a section judges by: §2.3's tables, reset at each section's start (``reset_key``) and changed only by that
# section's own workbook edits (``key + edit``, never what the app wrote: review S3, S4).
KEY = {}


def reset_key():
    """§2.3's key, fresh for a section: the modes, what each engages, where each slider stands, each slide's value per
    mode, each coupling's on-set, each mode's 30° row of the rear and front, each mode's ratio."""
    KEY.clear()
    KEY.update(modes=tuple(W8_MODES), engaged=dict(W8_ENGAGED), positions=copy.deepcopy(W8_POSITIONS),
               slides=copy.deepcopy(W8_SLIDES), couples=dict(W8_COUPLES), rows=copy.deepcopy(W8_REAR_FRONT),
               ratios=dict(W8_RATIOS))


reset_key()


def w8_turns(desk, mode):
    """§2.3's 30° row by shaft in ``mode``: the fixture's low range and the rear and front it shares."""
    return dict(W8_LOW[desk.a.spec.box.name], **KEY["rows"][mode])


def mode_of(desk, mode):
    """The read's ``ModeReport`` of ``mode`` (names compared as swbuild.on_in compares them), or None."""
    return next((m for m in desk.a.report.modes if swbuild.on_in((m.name,), mode)), None)


def box_paths(box):
    """Every SolidWorks document of the gearbox on record: the assembly, the layout part, the parts, the carriers."""
    return [box.assembly, box.layout] + sorted({c.part for c in box.components}) + [c.path for c in carriers_of(box)]


def body_ids(desk):
    """Every body the read places (gears, planet copies) and each carrier, by id."""
    return list(desk.a.report.layout.placed) + [wb_layout.carrier_id(c.shaft) for c in carrier_layouts(desk)]


def mode_expected(desk, mode, gears, input_gear, step, sense=1):
    """Each body's turn for ``step``° of the input in ``mode`` from §2.3's 30° row (``w8_turns``), never from the app
    (review S3): δ_g = sense · (step / 30) · row[shaft of g], about its own axis; a body whose shaft the row has
    free (None) is in the set returned, its δ 0. ``input_gear`` must be on the row's 30° shaft."""
    turns = w8_turns(desk, mode)
    w_in = turns[body_shaft(desk, input_gear)]
    free = {g for g in gears if turns[body_shaft(desk, g)] is None}
    return ({g: 0.0 if g in free else sense * step * turns[body_shaft(desk, g)] / w_in for g in gears}, free)


def app_mode_expected(desk, mode, gears, input_gear, step, sense=1):
    """W5's δ_i = sense · step · ω_i / ω_in with ``mode``'s own speeds (``ModeReport.motion``, the app's), about each
    body's own axis; a body whose shaft has no speed in ``mode`` is free there: its δ is 0 and it is in the set
    returned. Held against §2.3 before the build (``expect_modes_read``) and logged beside the key in the drive."""
    speeds = mode_of(desk, mode).motion.speeds
    w_in = speeds[body_shaft(desk, input_gear)]
    free = {g for g in gears if body_shaft(desk, g) not in speeds}
    return ({g: 0.0 if g in free else sense * step * float(speeds[body_shaft(desk, g)] / w_in) for g in gears},
            free)


def mode_wanted(desk, mode):
    """Every body's frame in ``mode`` from the read (``layout.frames_by_mode``: each slider at the mode's place, every
    other gear at the built turn), each carrier's (``layout.carrier_frame``, the same in every mode)."""
    frames = wb_layout.frames_by_mode(desk.a.report).get(mode, {})
    out = {g: (tuple(f.rotation), tuple(f.at)) for g, f in frames.items()}
    for carrier in carrier_layouts(desk):
        f = wb_layout.carrier_frame(carrier)
        out[wb_layout.carrier_id(carrier.shaft)] = (tuple(f.rotation), tuple(f.at))
    return out


def mode_record_frames(desk, mode):
    """Every body's frame on record for ``mode`` (schema 6's ``ComponentEntry.frames``; the one frame when a component
    has none of its own), each carrier's frame on record."""
    box = desk.record.gearbox
    out = {}
    for c in box.components:
        here = next((f for m, f in (c.frames or {}).items() if swbuild.on_in((m,), mode)), None)
        out[c.gear] = ((tuple(here["rotation"]), tuple(here["at"])) if here else (tuple(c.rotation), tuple(c.at)))
    out.update({wb_layout.carrier_id(c.shaft): (tuple(c.rotation), tuple(c.at)) for c in carriers_of(box)})
    return out


def key_suppressed(name, mode):
    """§2.3's flag for a mate in ``mode``: suppressed only for a coupling (``KEY["couples"]``) off there; every other mate
    of the gearbox, the slides, axes and spline (``W8_ALWAYS``) included, is on everywhere (review S4)."""
    return name in KEY["couples"] and not swbuild.on_in(KEY["couples"][name], mode)


def key_engaged(mode):
    """§2.3's (sleeve, dog) pairs ``mode`` engages, after the section's edits."""
    return next((v for m, v in KEY["engaged"].items() if swbuild.on_in((m,), mode)), ())


def key_off(mode):
    """§2.3's mates off in ``mode``: the couplings it does not engage."""
    return sorted(n for n in KEY["couples"] if key_suppressed(n, mode))


def key_slide(name, mode):
    """§2.3's value of the slide ``name`` in ``mode``, mm (``KEY["slides"]``)."""
    return next(v for m, v in KEY["slides"][name].items() if swbuild.on_in((m,), mode))


def off_in(box, mode):
    """The mates on record that are off in ``mode``: the per-mode ones (couplings, sliding meshes) not on there."""
    return sorted(m.name for m in box.mates if m.modes and not swbuild.on_in(tuple(m.modes), mode))


def flags_wanted(mate, configuration):
    """Whether a recorded mate should read suppressed in ``configuration``: only a per-mode mate off there."""
    return bool(mate.modes) and not swbuild.on_in(tuple(mate.modes), configuration)


def expect_modes_read(desk, label):
    """The read against W8-PLAN §2.3 before anything is built: no error (§2.2's "checks clean"; the strip's own
    warnings stay and are logged), the gate open, the four modes in order, what each engages, where each slider
    stands, each mode's speeds about each shaft's own axis (a free shaft has none), each mode's ratio, each slider's
    face span; the Speeds lines of each mode logged; then the app's kinematics against §2.3's 30° row for every body
    in every mode."""
    a = desk.a
    errors = [d.message for d in a.diagnostics if d.level == "error"]
    warnings = [d.message for d in a.diagnostics if d.level == "warning"]
    check(not errors and a.lay_out_refusal() == "", f"{label}: the workbook checks with no error and the gate is open: "
          f"errors {errors}, gate {a.lay_out_refusal()!r} ({len(warnings)} warning(s), logged above)")
    say(f"        header {a.report.worked_out_as!r}")
    names = [m.name for m in a.report.modes]
    check(names == list(KEY["modes"]), f"{label}: the modes are §2.3's, in order: {names}")
    for mode in KEY["modes"]:
        m = mode_of(desk, mode)
        if m is None:
            check(False, f"{label}: the read has no mode {mode}")
            continue
        check(tuple(map(tuple, m.engaged)) == KEY["engaged"][mode], f"{label}: {mode} engages {list(m.engaged)}")
        positions = {k: (v[0], float(v[1])) for k, v in m.positions.items()}
        check(positions == KEY["positions"][mode], f"{label}: {mode} places the sliders at {positions}")
        spans = {s: tuple(float(v) for v in getattr(p, "z_range", ())) for s, p in m.placed.items()}
        want_spans = {g: (KEY["slides"][f"{g} along Rear"][mode], KEY["slides"][f"{g} along Rear"][mode] + 8.0)
                      for g in ("RangeSlv", "ModeSlv")}
        check(spans == want_spans, f"{label}: {mode}'s slider face spans {spans} (§2.3: {want_spans})")
        speeds = {k: float(v) for k, v in m.motion.speeds.items()}
        turns = w8_turns(desk, mode)
        want = {s: 50.0 * t for s, t in turns.items() if t is not None}
        free = {s for s, t in turns.items() if t is None}
        check(all(s in speeds and abs(speeds[s] - v) <= 1e-9 * max(1.0, abs(v)) for s, v in want.items())
              and not free & set(speeds), f"{label}: {mode}'s speeds about each shaft's own axis are §2.3's "
              f"({want}, free {sorted(free)}): {speeds}")
        ratio = m.ratio
        check((ratio is None) == (KEY["ratios"][mode] is None) and (ratio is None or abs(float(ratio) - KEY["ratios"][mode])
                                                                <= 1e-9),
              f"{label}: {mode}'s ratio {ratio} ({m.ratio_why!r}; driven {m.driven}), §2.3's {KEY["ratios"][mode]}")
        try:
            lines, readout = ui_text.mode_speed_lines(a.spec, a.report, mode)
            for line in lines:
                say(f"speeds  {mode}  {line}")
            say(f"speeds  {mode}  readout {readout!r}")
        except Exception as exc:  # noqa: BLE001 - the words are C's, logged; the numbers are judged above
            say(f"speeds  {mode}  the Speeds lines raised {type(exc).__name__}: {exc}")
    for mode in KEY["modes"]:
        if mode_of(desk, mode) is None:
            continue
        gears = body_ids(desk)
        input_gear = next(g for g in gears if body_shaft(desk, g) == "In" and g in ("InPin", "Sun"))
        got, free = app_mode_expected(desk, mode, gears, input_gear, 30.0)
        turns = w8_turns(desk, mode)
        hand = {g: turns[body_shaft(desk, g)] for g in gears}
        bad = {g: (got[g], hand[g]) for g in gears if (hand[g] is None) != (g in free)
               or (hand[g] is not None and abs(got[g] - hand[g]) > 1e-9 * max(1.0, abs(hand[g])))}
        check(not bad, f"{label}: in {mode} the kinematics give §2.3's turns for +30° of {input_gear}, every body "
              f"(free: {sorted(free)}): " + (f"off {bad}" if bad else
                                             ", ".join(f"{g} {got[g]:+g}°" for g in gears if g not in free)))


def check_modes_plan(desk, label):
    """The plan's configurations, logged step by step (ops, on, off, values) and held to §2.3."""
    p = desk.plan
    mp = getattr(p, "modes_plan", None) if p is not None else None
    check(mp is not None and tuple(p.motion.modes) == KEY["modes"], f"{label}: the plan makes a configuration per mode: "
          f"{p.motion.modes if p is not None and p.motion is not None else None}")
    if mp is None:
        return
    for step in mp.steps:
        say(f"        mode {step.name}: makes {[op.name for op in step.ops]}; off {list(step.off)}; values "
            f"{dict(step.values)}")
    say(f"        same way {list(mp.same_way)}; check {mp.check(p.assembly)}")
    made = {op.name: step.name for step in mp.steps for op in step.ops}
    check(made == {n: on[0] for n, on in KEY["couples"].items()}, f"{label}: each coupling is made in the first mode it "
          f"is on in: {made}")
    check([dict(s.values) for s in mp.steps] == [{n: v[m] for n, v in KEY["slides"].items()} for m in KEY["modes"]],
          f"{label}: every slide's value per mode is §2.3's")


def check_modes_result(desk, result, label):
    """What the build says of each configuration (``GearboxResult.modes``, §1.8 steps 6 and 8): the four modes, every
    slide's value and every per-mode mate's flag as §2.3 has them, no clash and no interference error in any mode;
    the running version's positions finding on the result."""
    checks = list(getattr(result, "modes", []) or [])
    check([c.name for c in checks] == list(KEY["modes"]), f"{label}: the build checked every mode: "
          f"{[c.name for c in checks]}")
    for c in checks:
        say(f"        build's check of {c.name}: values {c.values}; flags {c.suppressed}; clashes "
            f"{[(x.gears, round(x.volume, 3)) for x in c.clashes]}; interference error {c.interference_error!r}; "
            f"mates {[(s.name, s.code, s.suppressed) for s in c.mates]}")
        values_ok = all(abs(float(c.values.get(n, float('nan'))) - v[c.name]) <= 1e-6 for n, v in KEY["slides"].items())
        flags_ok = all(c.suppressed.get(n) == (c.name not in on) for n, on in KEY["couples"].items())
        check(values_ok and flags_ok, f"{label}: the build read {c.name}'s slide values and coupling flags as §2.3 "
              "has them")
        stop_check(not c.clashes and not c.interference_error, f"{label}: the build found no interference in "
                   f"{c.name}: {[(x.gears, round(x.volume, 3)) for x in c.clashes]} {c.interference_error!r}")
    want = swcom.positions_per_configuration(TAG["revision"])
    got = getattr(result, "positions_per_configuration", None)
    check(got == want, f"{label}: the result carries this version's positions finding: {got} (findings {want})")


def check_modes_record(desk, label):
    """The record (schema 6) against §2.3: the modes as built; each SLIDE's value per mode; each coupling's on-set, its
    ratio 1 : 1 and its sense −1 (the same way, W8-INTERFACES §9.3); the always-on W8 mates on everywhere; no other
    mate per-mode; every component's frame in every mode the read's (each slider at the mode's place), and its one
    frame the first mode's."""
    box = desk.record.gearbox
    check(list(box.modes) == list(KEY["modes"]), f"{label}: the record holds the modes as built: {box.modes}")
    mates = {m.name: m for m in box.mates}
    for name, values in KEY["slides"].items():
        m = mates.get(name)
        got = {k: float(v) for k, v in (m.values if m else {}).items()}
        check(m is not None and m.kind == "slide" and got == values and not m.modes,
              f"{label}: {name} on record, a slide with §2.3's values {got}")
    for name, on in KEY["couples"].items():
        m = mates.get(name)
        check(m is not None and m.kind == "couple" and tuple(m.modes) == on and list(m.ratio) == [1, 1]
              and int(m.sense) == -1, f"{label}: {name} on record, a coupling on in {m and m.modes}, ratio "
              f"{m and m.ratio}, sense {m and m.sense}")
    for name, kind in W8_ALWAYS.items():
        m = mates.get(name)
        spline = kind == "spline"
        check(m is not None and m.kind == kind and not m.modes and not m.values
              and (not spline or (list(m.ratio) == [1, 1] and int(m.sense) == -1)),
              f"{label}: {name} on record, a {kind} mate on in every mode"
              + (f", ratio {m and m.ratio}, sense {m and m.sense} (§9 ruling 3: [1, 1], −1)" if spline else ""))
    per_mode = sorted(n for n, m in mates.items() if m.modes)
    check(per_mode == sorted(KEY["couples"]), f"{label}: the per-mode mates on record are the couplings: {per_mode}")
    first = box.modes[0] if box.modes else ""
    worst = (0.0, "")
    for mode in box.modes:
        want = mode_wanted(desk, mode)
        for c in box.components:
            f = c.frames.get(mode)
            gap = frame_gap(((f["rotation"]), f["at"]), want[c.gear]) if f and c.gear in want else float("inf")
            worst = max(worst, (gap, f"{c.gear} in {mode}"))
    check(worst[0] <= FRAME_TOLERANCE, f"{label}: every component's frame on record in every mode is the read's "
          f"(largest {worst[0]:.1e} at {worst[1] or '-'})")
    same = all(frame_gap((c.rotation, c.at), (c.frames[first]["rotation"], c.frames[first]["at"])) == 0.0
               for c in box.components if first in c.frames)
    check(same, f"{label}: every component's one frame on record is its frame in {first}, the mode it was saved in")


def modes_unshown(worker, desk, label, active):
    """§5's reads that show nothing: the configurations exactly the modes, ``active`` the active one; every recorded
    mate's flag in every configuration (``IsSuppressed2(3, …)``) and every slide's value in every configuration
    (``GetSystemValue3(3, …)``) against the record; the documents' marks before and after (SUPPRESSION_READ_MARKS
    and VALUE_READ_MARKS say "nothing": more is a NOTE)."""
    box = desk.record.gearbox
    configs = list(box.modes)
    names = [m.name for m in box.mates]
    slides = [m.name for m in box.mates if m.kind == "slide"]
    paths = box_paths(box)

    def work(s):
        out = {"flags_before": save_flags(s, paths), "configurations": s.configurations(),
               "active": s.active_configuration(), "flags": {}, "values": {}}
        for index, name in enumerate(names):
            s.find_mate(f"u{index}", name)
            out["flags"][name] = s.mate_suppression(f"u{index}", configs)
        for index, name in enumerate(slides):
            s.find_mate(f"v{index}", name)
            out["values"][name] = s.dimension_values(f"v{index}", configs)
        out["flags_after"] = save_flags(s, paths)
        return out
    out = run(worker, in_assembly(box.assembly, work))
    say(f"        configurations {out['configurations']}; active {out['active']}")
    for name in names:
        say(f"        flags {name}: " + ", ".join(f"{c} {'suppressed' if f else 'on'}"
                                                  for c, f in out["flags"][name].items()))
    for name in slides:
        say(f"        values {name}: {out['values'][name]}")
    check(sorted(out["configurations"]) == sorted(configs), f"{label}: the assembly's configurations are exactly the "
          f"modes, no template configuration left: {out['configurations']}")
    stop_check(swbuild.on_in((active,), out["active"]), f"{label}: the active configuration is {out['active']}, "
               f"{active} expected")
    wrong = [(m.name, c, out["flags"][m.name].get(c)) for m in box.mates for c in configs
             if out["flags"][m.name].get(c) != key_suppressed(m.name, c)]
    stop_check(not wrong, f"{label}: shown nothing, every mate's flag in every configuration is §2.3's (the couplings "
               f"on only where engaged, every other mate on): wrong {wrong}")
    bad = []
    for name in KEY["slides"]:
        for c in configs:
            want = key_slide(name, c)
            got = out["values"].get(name, {}).get(c)
            if got is None or got <= 0.0 or abs(got - want) > 1e-6:
                bad.append((name, c, got, want))
    stop_check(not bad, f"{label}: shown nothing, every slide's value in every configuration is §2.3's (none 0): "
               f"wrong {bad}")
    say(f"fact    {label}: GetSaveFlag before the reads {out['flags_before']}, after them {out['flags_after']}")
    check_marks(out["flags_after"], marked(out["flags_before"]), f"{label}: the flag and value reads")
    return out


def mode_state_job(box, mode, full=True):
    """A worker job: ``mode`` shown, the train rebuilt, its name read back; every body and the layout found again by
    Name2 and its frame read; with ``full``, every mated body's constrained status, the layout's and every fixed
    body's IsFixed (through those fresh handles), the mates (``mate_states``, anything else in the mate group) and
    ``interferences()``."""
    pairs = bodies(box) + [("layout", box.layout_component)]

    def work(s):
        s.show_configuration(mode)
        out = {"rebuilt": bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN)), "active": s.active_configuration(),
               "frames": {}, "names": {}, "status": {}, "fixed": {}}
        for index, (gear, name) in enumerate(pairs):
            s.find_component(f"q{index}", name)
            out["frames"][gear] = s.component_frame(f"q{index}")
            out["names"][name] = out["frames"][gear]
            if not full:
                continue
            if gear == "layout" or gear in box.fixed:
                out["fixed"][gear] = s.is_fixed(f"q{index}")
            else:
                out["status"][gear] = s.constrained_status(f"q{index}")
        if full:
            others = []
            out["states"] = [(m.name, m.code, m.warning, m.suppressed) for m in s.mate_states(others=others)]
            out["others"] = others
            out["clashes"] = s.interferences()
        return out
    return in_assembly(box.assembly, work)


def say_off(label, mode, live, wanted_frames):
    """Each body off its wanted frame, logged: its turn about its own axis from the wanted frame (degrees; None when
    it is not that frame turned about its own Z) and how far its origin stands from the wanted one."""
    off = []
    for body, frame in wanted_frames.items():
        if body in live and frame_gap(live[body], frame) > FRAME_TOLERANCE:
            turn = turn_degrees(frame[0], live[body][0])
            origin = max(abs(float(a) - float(b)) for a, b in zip(live[body][1], frame[1]))
            off.append(f"{body} turned {'off its axis' if turn is None else f'{turn:+.6f}°'}, origin off {origin:.3e} mm")
    say(f"fact    {label}: in {mode}, off the wanted frame: {off or 'none'}")


def judge_mode_frames(desk, label, mode, out, expected=None):
    """A mode's frames as read through fresh handles: the configuration shown reads back; every body at its frame on
    record for the mode to 1e-6, and that frame the read's; each slider's origin at its slide's value in the mode to
    1e-6 mm; the layout at identity."""
    box = desk.record.gearbox
    stop_check(swbuild.on_in((mode,), out["active"]), f"{label}: {mode} shown, the active configuration reads "
               f"{out['active']}")
    check(out["rebuilt"], f"{label}: the train's rebuild in {mode} answered True")
    live = out["frames"]
    record = mode_record_frames(desk, mode)
    want = mode_wanted(desk, mode)
    gap, at = frames_gap(live, record)
    if not stop_check(gap <= FRAME_TOLERANCE, f"{label}: every body stands at its frame on record for {mode} (largest "
                      f"{gap:.1e} at {at or '-'})"):
        say_off(label, mode, live, record)
    gap, at = frames_gap(record, want)
    check(gap <= FRAME_TOLERANCE, f"{label}: the frames on record for {mode} are the workbook's (largest {gap:.1e} at "
          f"{at or '-'})")
    if expected is not None:
        # After an Update: the frames the key and the workbook's edit give, worked by the script (never the app's).
        gap, at = frames_gap(live, expected[mode])
        if not stop_check(gap <= FRAME_TOLERANCE, f"{label}: every body stands where §2.3 and the edit put it in {mode} "
                          f"(largest {gap:.1e} at {at or '-'})"):
            say_off(label, mode, live, expected[mode])
    for name in KEY["slides"]:
        slider = name.split(" along ")[0]
        value = key_slide(name, mode)
        where = live[slider][1]
        stop_check(abs(float(where[2]) - value) <= 1e-6 and abs(float(where[0])) <= 1e-6
                   and abs(float(where[1])) <= 1e-6,
                   f"{label}: {slider} stands at {tuple(round(float(v), 9) for v in where)} mm in {mode}, on Rear's "
                   f"axis at its slide {name}'s §2.3 value {value:g} mm (off {abs(float(where[2]) - value):.1e})")
    lay = live["layout"]
    check(swbuild.same_frame(lay[0], lay[1], wb_layout.IDENTITY, (0.0, 0.0, 0.0)),
          f"{label}: the layout ({box.layout_component}) is at identity in {mode}")
    return live


def measure_mode(worker, desk, label, mode, expected=None):
    """§5's measurement of one mode, shown: its frames (``judge_mode_frames``); the mates exactly the record's and
    nothing else in the mate group; every mate on in the mode unsuppressed with code 0, every per-mode mate off in it
    reading suppressed (not judged by its code: GOTCHAS §103); every mated body ``GetConstrainedStatus`` 2; the layout
    and every fixed body IsFixed through fresh handles; no interference. Returns the read."""
    box = desk.record.gearbox
    started = time.monotonic()
    out = run(worker, mode_state_job(box, mode))
    live = judge_mode_frames(desk, label, mode, out, expected)
    off = set(key_off(mode))
    states = out["states"]
    say(f"        mates in {mode}: {states}; others {out['others']}; constrained {out['status']}; fixed {out['fixed']}")
    names = [s[0] for s in states]
    want = [m.name for m in box.mates]
    check(sorted(names) == sorted(want) and not out["others"], f"{label}: the mates are exactly the record's "
          f"{len(want)}, nothing else in the mate group: extra {sorted(set(names) - set(want))}, missing "
          f"{sorted(set(want) - set(names))}, others {out['others']}")
    wrong = [(s[0], s[3]) for s in states if (s[0] in off) != bool(s[3])]
    stop_check(not wrong, f"{label}: in {mode} the couplings §2.3 has off there read suppressed and every other mate "
               f"on: wrong {wrong}")
    bad = [(s[0], s[1], s[2]) for s in states if s[1] and not s[3]]
    check(not bad, f"{label}: every mate on in {mode} has error code 0: {bad}")
    loose = {g: v for g, v in out["status"].items() if v != findings.COMPONENT_UNDER_DEFINED}
    check(not loose, f"{label}: every mated body under-defined ({findings.COMPONENT_UNDER_DEFINED}) in {mode}: "
          f"{out['status']}")
    stop_check(out["fixed"] and all(out["fixed"].values()), f"{label}: the layout and every fixed body read IsFixed "
               f"in {mode} through handles fetched after the show: {out['fixed']}")
    gear_of = {n: g for g, n in bodies(box)}
    merged = swbuild._clashes(out["clashes"], gear_of)  # noqa: SLF001
    stop_check(not merged, f"{label}: no interference in {mode}: {[(c.gears, round(c.volume, 3)) for c in merged]}")
    say(f"        {mode} measured in {time.monotonic() - started:.1f} s; {memory()}")
    return out


def put_in_mode(box, mode, gear, rotation, at, locks):
    """A worker job: ``mode`` shown and rebuilt; every lock in ``locks`` suppressed in ``mode`` only
    (``set_mate_suppressed_in``) and the train rebuilt; ``gear`` put at (``rotation``, ``at``) with every gear mate
    left on (``findings.MESH_PHASE_ROUTE``), ``interferences()``; put back where it stood, ``interferences()``; the
    locks turned back on in ``mode`` and rebuilt, whatever happened; then each lock's flag in every configuration
    and every body's frame read."""
    name_of = dict(bodies(box))

    def work(s):
        out = {"errors": [], "cleanup": []}
        s.show_configuration(mode)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["active"] = s.active_configuration()
        held = []

        def all_frames(prefix):
            got = {}
            for index, (g, name) in enumerate(bodies(box)):
                s.find_component(f"{prefix}{index}", name)
                got[g] = s.component_frame(f"{prefix}{index}")
            return got
        try:
            for index, lock in enumerate(locks):
                s.find_mate(f"lock{index}", lock)
                held.append(index)                  # review N3: marked before the call, restored whatever it answers
                s.set_mate_suppressed_in(f"lock{index}", True, [mode])
            if locks:
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["unput"] = all_frames("u")
            s.find_component("moved", name_of[gear])
            before = s.component_frame("moved")
            s.place_component("moved", rotation, at, kind=swcom.ASSEMBLY_TRAIN)
            out["put"] = all_frames("p")             # the review's watch: does any body but the put one move?
            out["moved"] = s.interferences()
            s.place_component("moved", before[0], before[1], kind=swcom.ASSEMBLY_TRAIN)
            out["back"] = s.interferences()
        except Exception as exc:  # noqa: BLE001 - said; the locks still go back on below
            out["errors"].append(f"{type(exc).__name__}: {exc}")
            out["traceback"] = traceback.format_exc()
        finally:
            for index in held:
                try:
                    if s.mate_suppression(f"lock{index}", [mode])[mode]:
                        s.set_mate_suppressed_in(f"lock{index}", False, [mode])
                except Exception as exc:  # noqa: BLE001
                    out["cleanup"].append(f"{locks[index]} back on: {type(exc).__name__}: {exc}")
            if locks:
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["restored"] = s.interferences() if not out["errors"] else None
        out["locks"] = {lock: s.mate_suppression(f"lock{index}", list(box.modes)) for index, lock in enumerate(locks)
                        if index in held}
        out["frames"] = {}
        for index, (g, name) in enumerate(bodies(box)):
            s.find_component(f"f{index}", name)
            out["frames"][g] = s.component_frame(f"f{index}")
        return out
    return in_assembly(box.assembly, work)


def mode_put_control(worker, desk, label, mode, gear, partners, locks):
    """One half-pitch control in ``mode``: ``gear`` turned half its pitch about its own axis from its frame on record
    for the mode (``put_in_mode``) must clash with exactly ``partners`` (none, for an empty set) and nothing else; put
    back, no interference; every lock back on in every configuration; every body at its frame on record for the mode
    to 1e-6."""
    box = desk.record.gearbox
    rotation, at = mode_record_frames(desk, mode)[gear]
    pitch = wb_layout.pitch(desk.a.report.layout.placed[gear])
    started = time.monotonic()
    out = run(worker, put_in_mode(box, mode, gear, turn_about_z(rotation, pitch / 2), at, locks))
    for line in out.get("traceback", "").splitlines():
        say("        " + line)
    gear_of = {n: g for g, n in bodies(box)}
    check(not out["errors"] and not out["cleanup"] and swbuild.on_in((mode,), out["active"]),
          f"{label}: {gear}'s control ran in {out['active']}: {out['errors']} {out['cleanup']}")
    frame_none_stop(out["errors"] + out["cleanup"], label)
    if "put" in out and "unput" in out:
        others = {g: frame_gap(out["put"][g], out["unput"][g]) for g in out["put"] if g != gear}
        moved = {g: f"{v:.1e}" for g, v in others.items() if v > FRAME_TOLERANCE}
        turned = turn_degrees(out["unput"][gear][0], out["put"][gear][0])
        say(f"fact    {label}: the put turned {gear} {turned if turned is None else f'{turned:+.6f}'}°; other bodies "
            f"moved by it (beyond 1e-6): {moved or 'none'}")
    merged = swbuild._clashes(out.get("moved", []), gear_of)  # noqa: SLF001
    said = [(c.gears, round(c.volume, 3)) for c in merged]
    pairs = {frozenset(c.gears) for c in merged if c.volume > 0}
    wanted_pairs = {frozenset((gear, p)) for p in partners}
    if partners:
        stop_check("moved" in out and pairs == wanted_pairs and len(pairs) == len(merged),
                   f"{label}: {gear} turned half a pitch ({pitch / 2:.4f}°){f' with {locks} suppressed in {mode}' if locks else ''} "
                   f"clashes with exactly {sorted(partners)}: {said}")
    else:
        check("moved" in out and not merged, f"{label}: {gear}, disengaged in {mode}, turned half a pitch "
              f"({pitch / 2:.4f}°){f' with {locks} suppressed in {mode}' if locks else ''} clashes with nothing: {said}")
    back = swbuild._clashes(out.get("back", []), gear_of)  # noqa: SLF001
    stop_check("back" in out and not back, f"{label}: {gear} put back, no interference in {mode} "
               f"({time.monotonic() - started:.1f} s): {[(c.gears, round(c.volume, 3)) for c in back]}")
    restored = swbuild._clashes(out.get("restored") or [], gear_of)  # noqa: SLF001
    check(out.get("restored") is not None and not restored, f"{label}: the locks back on after {gear}'s control, no "
          f"interference (review N4): {[(c.gears, round(c.volume, 3)) for c in restored]}")
    left = {lock: [c for c, f in flags.items() if f] for lock, flags in out["locks"].items()}
    check(len(out["locks"]) == len(locks) and not any(left.values()),
          f"{label}: no lock left suppressed in any configuration: {left}")
    gap, where = frames_gap(out["frames"], mode_record_frames(desk, mode))
    check(gap <= FRAME_TOLERANCE, f"{label}: after {gear}'s control every body at its frame on record for {mode} "
          f"(largest {gap:.1e} at {where or '-'})")
    return out


def coupling_controls(worker, desk, label, mode):
    """§5's half-pitch control on each coupling ``mode`` engages: the dog put half its pitch (6°) with the coupling on
    and every lock touching the dog suppressed in this configuration around the put, which must clash with its
    sleeve only; put back, none. A disengaged dog, turned the same, clashes with nothing."""
    box = desk.record.gearbox
    engaged = {dog: sleeve for sleeve, dog in key_engaged(mode)}
    for dog in [g.id for g in desk.a.spec.gears if g.kind == "dog"]:
        guard()
        locks = [m.name for m in box.mates if m.kind == "lock" and dog in m.gears]
        sleeve = engaged.get(dog)
        mode_put_control(worker, desk, f"{label}, {'the coupling ' + sleeve + '–' + dog if sleeve else dog}", mode,
                         dog, {sleeve} if sleeve else set(), locks)


def mesh_controls(worker, desk, label, mode):
    """W5's and W7's half-pitch controls on the listed meshes, in ``mode`` (the meshes are on in every mode): for each
    mesh at copy level the gear W5 chooses (the one in that mesh alone, never a fixed one, one in no lock if there is
    one, else with every lock touching either gear suppressed in ``mode``), turned half its pitch, must clash with
    exactly the gears it meshes with."""
    box = desk.record.gearbox
    placed = desk.a.report.layout.placed
    meshes = wb_geometry.expand_meshes(desk.a.spec, placed)
    count = {g: sum(g in m for m in meshes) for m in meshes for g in m}
    locked = {g for m in box.mates if m.kind == "lock" for g in m.gears}
    chosen = {}
    for a, b in meshes:
        order = [g for g in ([b, a] if count[b] == 1 else [a, b]) if g not in box.fixed]
        if not order:
            continue
        free = [g for g in order if g not in locked]
        gear, locks = ((free[0], []) if free else
                       (order[0], [m.name for m in box.mates if m.kind == "lock" and (a in m.gears or b in m.gears)]))
        chosen.setdefault(gear, locks)
    for gear, locks in chosen.items():
        guard()
        partners = {y if x == gear else x for x, y in meshes if gear in (x, y)}
        mode_put_control(worker, desk, f"{label}, mesh control on {gear}", mode, gear, partners, locks)


def measure_modes(worker, desk, label, controls=True, active=None, expected=None):
    """W8-PLAN §5, "what every mode gets measured": the reads that show nothing (``modes_unshown``), then each mode
    shown and measured (``measure_mode``) with, given ``controls``, its couplings' half-pitch controls and the listed
    meshes'; after the controls, every mode shown again and its frames read, so a control is
    seen to have touched no other mode. The mesh controls run in every mode (review S1: N has no engaged coupling, so
    without them nothing in N would show that the interference read can see a clash). Returns each mode's read."""
    box = desk.record.gearbox
    say(f"measure {label}: every mode ({', '.join(box.modes)}); controls {controls}; {memory()}")
    modes_unshown(worker, desk, label, active or box.modes[0])
    reads = {}
    for mode in box.modes:
        guard()
        reads[mode] = measure_mode(worker, desk, f"{label}, in {mode}", mode, expected)
        if controls:
            started = time.monotonic()
            mesh_controls(worker, desk, f"{label}, in {mode}", mode)        # review S1: a positive control in every mode
            coupling_controls(worker, desk, f"{label}, in {mode}", mode)
            say(f"        {mode}'s controls in {time.monotonic() - started:.1f} s; {memory()}")
    if controls:
        for mode in box.modes:
            guard()
            out = run(worker, mode_state_job(box, mode, full=False))
            judge_mode_frames(desk, f"{label}, in {mode} after every mode's controls", mode, out, expected)
    return reads


def mode_drive_proof(worker, desk, label, mode, control=None):
    """W8-PLAN §5's driven proof in ``mode`` (the script's, never the app's): ``drive_job`` with the mode shown, W5's
    angle mate on the input's anchor, "Drive" 90 -> 120; every body's turn about its own axis against the mode's
    kinematics (§2.3's 30° row, pinned before the build) to 1e-6 relative, sign included, the sleeves and dogs
    included; a body free in the mode must not turn (more than 1e-6 is a NOTE); every body where the kinematics put
    it (a planet copy carried round its carrier), every listed mesh, every coupling the mode engages and the spline in
    step; no interference with the drive at 120. ``control`` (the recorded gear mate's name, the gear its Flip
    decides): the both-Flips control — the recorded mate suppressed in this mode, a 1 : 1 gear mate made in its place
    with each Flip, read by the app, driven; exactly one Flip must turn every body right, the other the decided gear
    the mirror way, and the app's read must name the right one, else a STOP (the run halts). Then M12's hygiene, and
    every mate's flag in every configuration as recorded."""
    box, components, gears, input_gear = drive_inputs(desk)
    say(f"drive   {label}: input {input_gear}; mode {mode}; both-Flips control {control}; {memory()}")
    plane, ruled = drive_assumptions(desk, input_gear, label)
    spec, entry, judge = None, None, ""
    if control is not None:
        name, judge = control
        entry = next(m for m in box.mates if m.name == name)
        a, b = entry.gears
        axes = gear_axes(frames_on_record(desk), a, b)
        # W8-INTERFACES §9 ruling 3: a SPLINE's sense is −1 and a COUPLE's −σ_S·σ_D, −1 for these Z+ shafts: both turn
        # their gears the same way, from the key and not from the record (review S4).
        spec = {"a": a, "b": b, "mesh": name, "ratio": (1, 1), "axes": axes, "same": True, "clash": True,
                "turned": False}
    started = time.monotonic()
    out = run(worker, drive_job(box.assembly, components, box.layout_component, input_gear, control=spec,
                                fixed=box.fixed, plane=plane, clash_driven=True, mode=mode, configs=list(box.modes)))
    say(f"        in {time.monotonic() - started:.1f} s; drive route {out.get('route')!r}; rebuilds {out['rebuilds']}; "
        f"drive mate {out.get('drive_mate')}; control mate {out.get('control_mate')}")
    if "link_refused" in out:
        say(f"fact    {label}: the drive's link to the global {DRIVE} was refused with {len(box.modes)} configurations "
            f"({out['link_refused']}); {DRIVE} moved by the angle mate's own value in {mode} instead")
    if out.get("route") == "value":
        say(f"ROUTE   {label}: the DRIVE RAN BY THE VALUE ROUTE, not W5's global (a ruling for the coordinator): the angle "
            f"mate's own D1 set in {mode} by SetSystemValue3; (value set, read back in degrees, input's R[0:2]) "
            f"{out.get('route_reads')}")
    elif out.get("route") == "global":
        say(f"fact    {label}: the drive ran by W5's global {DRIVE}, its link accepted with {len(box.modes)} "
            "configurations")
    for line in out.get("traceback", "").splitlines():
        say("        " + line)
    check(not out["errors"], f"{label}: the drive ran without a raise: {out['errors']}")
    check(not out["cleanup"], f"{label}: every cleanup step ran: {out['cleanup']}")
    frame_none_stop(out["errors"] + out["cleanup"], label)
    stop_check(swbuild.on_in((mode,), out.get("active", "")), f"{label}: {mode} shown for the drive, the active "
               f"configuration reads {out.get('active')}")
    built = out.get("built")
    if built is None:
        raise Halt(f"{label}: the drive could not even read the built frames: {out['errors']}")
    record = mode_record_frames(desk, mode)
    gap, at = frames_gap(built, record)
    check(gap <= FRAME_TOLERANCE, f"{label}: before the drive every body stands at its frame on record for {mode} "
          f"(largest {gap:.1e} at {at or '-'})")
    if "added" not in out:
        raise Halt(f"{label}: the 90° drive could not be added: {out['errors']}")
    gap, at = frames_gap(out["added"], built)
    if gap > FRAME_TOLERANCE:
        raise Halt(f"{label}: adding the 90° drive moved {at} by {gap:.1e} (W5-PLAN §4.2: stop and ask)")
    check(True, f"{label}: adding the 90° drive moved nothing (largest {gap:.1e})")
    step = DRIVE_TO - DRIVE_FROM
    expected, free = mode_expected(desk, mode, gears, input_gear, step, 1 if ruled is None else ruled)
    gear_of = {n: g for g, n in components}
    if "driven" in out:
        turns = {g: turn_degrees(built[g][0], out["driven"][g][0]) for g in gears}
        sense = input_sense(label, turns, input_gear, step, ruled)
        expected, free = mode_expected(desk, mode, gears, input_gear, step, sense)
        app_exp, app_free = app_mode_expected(desk, mode, gears, input_gear, step, sense)
        differ = {g: (expected[g], app_exp[g]) for g in gears
                  if (g in free) != (g in app_free) or abs(expected[g] - app_exp[g]) > 1e-9 * max(1.0, abs(expected[g]))}
        say(f"        §2.3's key against the app's kinematics in {mode}: "
            + (f"DIFFER {differ}" if differ else "the same for every body, the free ones alike"))
        say_turns(f"{DRIVE} {DRIVE_FROM:g} -> {DRIVE_TO:g} in {mode} (expected from §2.3's key)", turns, expected)
        for g in gears:
            if g not in free:
                stop_check(close_turn(turns[g], expected[g]), f"{label}: {g} turned "
                           f"{turns[g] if turns[g] is None else f'{turns[g]:+.9f}'}° for {expected[g]:+.9f}° in {mode}, "
                           f"sign included (off {'-' if turns[g] is None else f'{abs(turns[g] - expected[g]):.1e}'})")
            elif turns[g] is None:
                check(False, f"{label}: {g}, free in {mode}, left its axis when the input was driven")
            elif abs(turns[g]) > DRIVE_TOLERANCE:
                note(f"{label}: {g}, free in {mode}, turned {turns[g]:+.9f}° when the input was driven (W8-PLAN §5: an "
                     "unconnected train is the solver's to leave)")
        say(f"        free in {mode}, standing still to {DRIVE_TOLERANCE:g}°: "
            f"{sorted(g for g in free if turns[g] is not None and abs(turns[g]) <= DRIVE_TOLERANCE)}")
        want = expected_frames(desk, built, expected)
        gaps = {g: frame_gap(out["driven"][g], want[g]) for g in gears if g not in free}
        check(all(v <= FRAME_TOLERANCE for v in gaps.values()), f"{label}: driven, every body where the kinematics put "
              f"it, on its axis and in its place (planet copies carried round): largest "
              f"{max(gaps.values()) if gaps else 0.0:.1e} at {max(gaps, key=gaps.get) if gaps else '-'}")
        residuals = mesh_residuals(desk, built, out["driven"])
        check(all(abs(r) <= 1e-6 for _, _, r in residuals), f"{label}: every listed mesh in step driven in {mode}: "
              f"{[(a, b, f'{r:.1e} rad') for a, b, r in residuals]}")
        pairs = list(key_engaged(mode)) + [W8_SPLINE]
        steps_off = {f"{x}–{y}": (None if turns[x] is None or turns[y] is None else turns[x] - turns[y])
                     for x, y in pairs}
        check(all(steps_off[f"{x}–{y}"] is not None
                  and abs(steps_off[f"{x}–{y}"]) <= DRIVE_TOLERANCE * max(1.0, abs(expected[x])) for x, y in pairs),
              f"{label}: each coupling {mode} engages and the spline turn their two gears together: "
              f"{({k: (None if v is None else f'{v:.1e}°') for k, v in steps_off.items()})}")
        merged = swbuild._clashes(out.get("driven_clash") or [], gear_of)  # noqa: SLF001
        check(out.get("driven_clash") is not None and not merged, f"{label}: interferences() with {DRIVE} at "
              f"{DRIVE_TO:g} in {mode}: none: {[(c.gears, round(c.volume, 3)) for c in merged]}")
        say(f"        states driven: {out.get('states_driven')}")
        check(not [s for s in out.get("states_driven", []) if s[1] and not s[3]],
              f"{label}: no mate on in {mode} in error while driven")
    if "back" in out:
        gap, at = frames_gap(out["back"], built)
        check(gap <= FRAME_TOLERANCE, f"{label}: {DRIVE} set back to {DRIVE_FROM:g}, every body at its built frame "
              f"(largest {gap:.1e} at {at or '-'})")
    halt = ""
    if entry is not None:
        flips = [f for f in (True, False) if f"control_driven {f}" in out]
        right, wrong = [], []
        if len(flips) == 2:
            for flip in flips:
                gap, at = frames_gap(out[f"control_added {flip}"], built)
                check(gap <= FRAME_TOLERANCE, f"{label}, control: the 1 : 1 gear mate with Flip {flip} moved nothing "
                      f"when made (largest {gap:.1e})")
                turns = {g: turn_degrees(built[g][0], out[f"control_driven {flip}"][g][0]) for g in gears}
                say_turns(f"control, {CONTROL + entry.name} with Flip {flip}", turns, expected)
                if all(close_turn(turns[g], expected[g]) for g in gears if g not in free):
                    right.append(flip)
                elif (turns[judge] is not None and close_turn(turns[judge], -expected[judge])
                      and abs(expected[judge]) > 1e-3):
                    wrong.append(flip)
                found = out.get(f"control_clash {flip}")
                said = [(c.gears, round(c.volume, 3)) for c in swbuild._clashes(found or [], gear_of)]  # noqa: SLF001
                say(f"fact    {label}, control: driven {step:g}° with Flip {flip} "
                    f"({'right' if flip in right else 'wrong' if flip in wrong else 'neither'}): interference {said}")
                gap, at = frames_gap(out[f"control_back {flip}"], built)
                check(gap <= FRAME_TOLERANCE, f"{label}, control: {DRIVE} set back with Flip {flip}'s mate on: every "
                      f"body at its built frame (largest {gap:.1e} at {at or '-'})")
            ok = len(right) == 1 and len(wrong) == 1
            stop_check(ok, f"{label}, control: exactly one Flip turns every body right ({right}) and the other turns "
                       f"{judge} the mirror way ({wrong})")
            if not ok:
                halt = f"{label}: the both-Flips control on {entry.name} told no right Flip from a wrong one"
            for flip in flips:
                read = out.get(f"control_read {flip}")
                if read is None:
                    stop_check(False, f"{label}, control: the mate with Flip {flip} was not read")
                    halt = halt or f"{label}: a control mate was not read"
                    continue
                say_read(f"{label}, control with Flip {flip}", read)
                app = read.get("app")
                agree = app is not None and ok and bool(app[0]) == (flip in right)
                stop_check(agree, f"{label}, control: the app's read of the mate with Flip {flip} says right "
                           f"{app[0] if app is not None else read.get('app_error')}; the drive says {flip in right}")
                if not agree:
                    halt = halt or f"{label}: the app's read of the control mate disagrees with the drive"
            held = TURNED.get(os.path.normcase(box.assembly), set())
            made_with = (not bool(findings.GEAR_MATE_FLIP)) if entry.name in held else bool(findings.GEAR_MATE_FLIP)
            year = {34: 2026, 32: 2024}.get(TAG["major"], TAG["major"])
            needed = getattr(findings, f"COLLINEAR_GEAR_MATE_FLIP_NEEDED_ON_{year}", None)
            say(f"fact    {label}: {entry.name} turns right with Flip {right} here on SolidWorks "
                f"{TAG['version'] or TAG['major']} (collinear axes; findings.GEAR_MATE_FLIP {findings.GEAR_MATE_FLIP}, "
                f"the spike's spline needed Flip {needed} on {year}); the build's read-back left the recorded mate with "
                f"Flip {made_with} ({'turned round' if entry.name in held else 'as first made'}, by the build's "
                "turned_round)")
        else:
            stop_check(False, f"{label}, control: never driven with both Flips: {out['errors']}")
            halt = f"{label}: the both-Flips control on {entry.name} did not run"
        if "control_gone" in out:
            gap, at = frames_gap(out["control_gone"], built)
            check(gap <= FRAME_TOLERANCE, f"{label}, control: the control mates deleted and {entry.name} back on in "
                  f"{mode}: every body at its built frame (largest {gap:.1e} at {at or '-'})")
    # M12, before anything is saved
    if "after" in out:
        gap, at = frames_gap(out["after"], built)
        check(gap <= FRAME_TOLERANCE, f"{label}: the drive gone, every frame against the built frames (largest "
              f"{gap:.1e} at {at or '-'})")
        check(out["equations_after"] == out["equations_before"] and not any(
            equations.quote(DRIVE) in t for t in out["equations_after"]),
              f"{label}: no {DRIVE} equation left: {[t for t in out['equations_after'] if t not in out['equations_before']]}")
        names = [s[0] for s in out["states_after"]]
        check(names == out["mates_before"] and DRIVE_MATE not in names and not any(n.startswith(CONTROL)
                                                                                   for n in names),
              f"{label}: no angle mate or control mate left; the mates as before: {names}")
        off = sorted(s[0] for s in out["states_after"] if s[3])
        check(off == key_off(mode), f"{label}: suppressed in {mode} exactly the couplings §2.3 has off there, no lock: "
              f"{off}")
        check(not [s for s in out["states_after"] if s[1] and not s[3]], f"{label}: no mate on in {mode} in error "
              "after the drive")
        check(all(v == findings.COMPONENT_UNDER_DEFINED for v in out["constrained_after"].values()),
              f"{label}: every mated body under-defined again: {out['constrained_after']}")
        flags = out.get("flags_after")
        wrong = ([(n, c, f) for n, by in flags.items() for c, f in by.items() if f != key_suppressed(n, c)]
                 if flags is not None else None)
        stop_check(flags is not None and not wrong, f"{label}: after the drive every mate's flag in every "
                   f"configuration is §2.3's: wrong {wrong}")
    else:
        check(False, f"{label}: the state after the drive could not be read: {out['cleanup']}")
    if halt:
        raise Halt(halt)
    return out


def reopen_modes(worker, desk, label):
    """§5's reopen: the first mode shown (the assembly reopens in the configuration saved active), this run's
    documents saved and closed; opened: every document unmodified straight after the open, the first mode active;
    then the flags, values and every mode's frames, mates and interference measured again (no controls); and the
    first mode shown and rebuilt last, so the assembly is left (and on 2024 kept) in the mode it opens in."""
    box = desk.record.gearbox
    first = box.modes[0]

    def show_first(s):
        s.show_configuration(first)
        return bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN)), s.active_configuration()
    say(f"reopen  {label}: {first} shown before the save: {run(worker, in_assembly(box.assembly, show_first))}")
    left = run(worker, close_ours)
    check(not left, f"{label}: saved and closed this run's documents: left {left}")
    say(f"        open now: {run(worker, open_titles)}")
    paths = box_paths(box)
    run(worker, lambda s: live_open(s, box.assembly))
    flags = run(worker, lambda s: save_flags(s, paths))
    check(len(flags) == len(paths) and not marked(flags), f"{label}, reopened: every document just opened from its "
          f"file reads GetSaveFlag False: {flags}")
    active = run(worker, in_assembly(box.assembly, lambda s: s.active_configuration()))
    stop_check(swbuild.on_in((first,), active), f"{label}, reopened: it opens in {active}, the first mode {first} "
               "expected (REOPENS_IN_SAVED_CONFIGURATION)")
    say(f"fact    {label}, reopened: marked modified after the active configuration's read: "
        f"{marked(run(worker, lambda s: save_flags(s, paths)))}")
    measure_modes(worker, desk, f"{label}, reopened", controls=False)
    # Review S2: what is left (and what end_clean saves on 2024) is the assembly in its first mode, as the record says.
    left_in = run(worker, in_assembly(box.assembly, show_first))
    stop_check(left_in[0] and swbuild.on_in((first,), left_in[1]), f"{label}: left with {first} shown and the train "
               f"rebuilt: {left_in}")


def raw_flag_reads(worker, desk, label, names=None):
    """The coordinator's widening of review N2: for every coupling and one slide, a RAW ``IFeature.IsSuppressed2(3,
    GetConfigurationNames())`` paired in document order (W8's run 1: it answers in that order), beside the app's own
    per-name read (``mate_suppression``), both held to §2.3; and one raw read with the names reversed, logged as a
    fact, to show on each run whether SolidWorks still answers in document order. Shows nothing; the marks logged."""
    box = desk.record.gearbox
    names = list(names or (list(KEY["couples"]) + ["RangeSlv along Rear"]))
    paths = box_paths(box)

    def work(s):
        out = {"flags_before": save_flags(s, paths), "configurations": s.configurations(), "raw": {}, "reversed": {},
               "app": {}}
        order = out["configurations"]
        for index, name in enumerate(names):
            feature = s._mate_feature(name)  # noqa: SLF001 - the raw call, beside the app's
            out["raw"][name] = swcom._per_name(call(feature, "IsSuppressed2", findings.SPECIFY_CONFIGURATIONS,  # noqa: SLF001
                                                    s._names(order)))  # noqa: SLF001
            out["reversed"][name] = swcom._per_name(call(feature, "IsSuppressed2", findings.SPECIFY_CONFIGURATIONS,  # noqa: SLF001
                                                         s._names(list(reversed(order)))))  # noqa: SLF001
            s.find_mate(f"raw{index}", name)
            out["app"][name] = s.mate_suppression(f"raw{index}", order)
        out["flags_after"] = save_flags(s, paths)
        return out
    out = run(worker, in_assembly(box.assembly, work))
    order = out["configurations"]
    say(f"        raw reads, GetConfigurationNames {order}")
    for name in names:
        raw = dict(zip(order, [bool(f) for f in out["raw"][name]]))
        app = {c: bool(f) for c, f in out["app"][name].items()}
        want = {c: key_suppressed(name, c) for c in order}
        say(f"read    {label}: {name}: raw in document order {raw}; the app per name {app}; §2.3 {want}")
        stop_check(len(out["raw"][name]) == len(order) and raw == want, f"{label}: the raw IsSuppressed2 of {name}, "
                   "paired in document order, is §2.3's")
        stop_check(app == want, f"{label}: the app's per-name read of {name} is §2.3's")
        rev = [bool(f) for f in out["reversed"][name]]
        in_doc = rev == [raw[c] for c in order]
        in_passed = rev == [raw[c] for c in reversed(order)]
        say(f"fact    {label}: {name}, names passed reversed {list(reversed(order))}: answered {rev} — "
            + ("in document order, as on run 1" if in_doc and not in_passed else
               "in the order passed" if in_passed and not in_doc else
               "the same either way (every flag alike)" if in_doc and in_passed else "in neither order"))
    check_marks(out["flags_after"], marked(out["flags_before"]), f"{label}: the raw flag reads")


def modes_built(worker, desk, label, after_build=None):
    """A W8 fixture built fresh through the app and judged (W8-PLAN §5 s0 and s1): the plan's configurations; built
    to turn (W5's checks: saved, no interference, the marks, the footer); the build's own per-mode checks and the
    record against §2.3; every mode measured with the coupling and mesh controls; W7's carrier part read as a
    skeleton; the driven proof in every mode, the both-Flips controls in 4H and 4L; reopened and measured again."""
    check_modes_plan(desk, label)
    started = time.monotonic()
    plan, result = build_turning(worker, desk, label, None, None)
    say(f"fact    {label}: the build, its checks and its saves took {time.monotonic() - started:.1f} s")
    asm = result.assembly
    said = [desk.note[0]] + list(result.log_lines()) + list(asm.mate_problems if asm else [])
    check(not any("where the mode has it" in line for line in said), f"{label}: no \"reads … where the mode has it …\" "
          "sentence in the build's words")
    both = [p for p in (asm.mate_problems if asm else []) if "whichever way" in p]
    if both:
        STOPS.append(f"{label}: a gear mate reads wrong both ways round: {both}")
        say("STOP    W8-PLAN §0.5: a coupling or spline gear mate reads wrong both ways round (J8 then needs a probe)")
    if not result.ok or desk.record is None or desk.record.gearbox is None or not desk.record.gearbox.assembly:
        # Refused (W5's answer 1: nothing saved, the document left open): nothing below has an assembly to measure.
        # The refused, never-saved document is this run's, so close_ours closes it by its title (as m4's).
        if asm is not None and asm.document and not asm.saved:
            REFUSED.append(asm.document)
        say(f"        mate problems {asm.mate_problems if asm else None}; failures {asm.failures if asm else None}; "
            f"left open as {asm.document if asm else None!r}")
        raise AssertionError(f"{label}: the build saved no assembly, so the section stops here: {desk.note[0]}")
    check_modes_result(desk, result, label)
    check_modes_record(desk, label)
    if after_build is not None:            # s4's Build again…: the earlier files read before anything else is touched
        after_build()
    box = desk.record.gearbox
    raw_flag_reads(worker, desk, f"{label} built")
    reads = measure_modes(worker, desk, f"{label} built", controls=True)
    if carriers_of(box):
        carrier_part_check(worker, desk, f"{label} built, in {box.modes[0]}", reads[box.modes[0]]["names"])
    for mode in box.modes:
        guard()
        control = next(((name, judge) for m, name, judge in W8_FLIP_CONTROLS if swbuild.on_in((m,), mode)), None)
        mode_drive_proof(worker, desk, f"{label} built, driven in {mode}", mode, control)
    reopen_modes(worker, desk, f"{label} built")
    return plan, result


def s_blocked(section):
    """A later W8 section that starts from s1.master is not run when s1's build failed."""
    if W8_MASTER["failed"]:
        check(False, f"{section}: not run: s1's build of the E4 transfer case failed ({W8_MASTER['failed']}), and "
                     "every later W8 section starts from it")
        return True
    return False


def section_s0(worker, excel):
    say("== s0  TransferCase_Parallel (W8-PLAN §2.2, §5), the shakedown, W7-free: the sleeve and dog kinds built, a "
        "configuration per mode (2H, 4H, N, 4L); every mode measured with its couplings' half-pitch controls; the "
        "driven proof in every mode, the both-Flips controls on the spline in 4H and on RangeSlv engages LoDog in 4L; "
        "reopen")
    folder, path, book, desk = write_fixture(worker, excel, "s0", spec_parallel, keep="TransferCase_Parallel.xlsx")
    expect_modes_read(desk, "s0")
    modes_built(worker, desk, "s0")


def section_s1(worker, excel):
    say("== s1  the E4 transfer case (W8-PLAN §2.1, §5): E3's 4 : 1 planetary as the low range, LoDog on the carrier; "
        "built fresh (the one E4 build); every mode measured with its couplings' half-pitch controls; the driven proof "
        "in every mode with the both-Flips controls in 4H and 4L; reopen; then kept as s1.master")
    fails, stops = len(FAILS), len(STOPS)
    folder, path, book, desk = write_fixture(worker, excel, "s1", spec_e4, keep="TransferCase_E4.xlsx")
    expect_modes_read(desk, "s1")
    try:
        modes_built(worker, desk, "s1")
    except (Halt, Stopped):
        W8_MASTER["failed"] = "halted"
        raise
    except Exception as exc:
        W8_MASTER["failed"] = f"{type(exc).__name__}: {exc}"
        raise
    if len(FAILS) > fails or len(STOPS) > stops:
        # Review S6: nothing is built on an s1 that failed or hit a STOP; its folder stays as it is, for the log.
        W8_MASTER["failed"] = f"{len(FAILS) - fails} failed, {len(STOPS) - stops} STOP(s)"
        say(f"master  s1 is not kept as s1.master ({W8_MASTER['failed']}); its folder stays s1, for the log")
        return
    keep_master(worker, folder, "s1")

# -- W8 s2, s3, s4: each from a copy of s1.master (W8-PLAN §5, J24) ------------------------------------------------


def column_letter(col):
    out = ""
    while col:
        col, rem = divmod(col - 1, 26)
        out = chr(65 + rem) + out
    return out


def cell(book, sheet, header, key):
    """The A1 address of the cell of ``sheet`` under the column whose row-1 header starts with ``header``, in the row
    whose first column reads ``key`` — or, ``key`` empty, the first row whose first column is empty."""
    ws = book.wb.Worksheets(sheet)
    col = next(c for c in range(1, 60) if str(ws.Cells(1, c).Value or "").startswith(header))
    row = next(r for r in range(2, 400) if str(ws.Cells(r, 1).Value or "").strip() == key)
    return f"{column_letter(col)}{row}"


def start_w8_copy(worker, excel, section):
    """A W8 copy section's start: ``copy_built`` of ``s1.master`` in this run's output folder, read through the window's
    own path, the key reset. The coordinator's ruling (stage 2a): a copy that asks anything or resolves a reference
    outside the copy is a STOP, never a fresh build; so is a missing master. Returns the folder, the workbook, its Excel
    book, the desk, and every body's frame on record per mode as copied (the built frames)."""
    reset_key()
    master = os.path.join(OUT, "s1" + MASTER_SUFFIX)
    if not os.path.isdir(master) or s_blocked(section):
        stop_check(False, f"{section}: no usable s1.master in the run's output folder ({master}), and a W8 section "
                          "starts only from a copy of it")
        raise Halt(f"{section}: no s1.master to copy")
    try:
        folder = copy_built(master, section)
    except CopyStop as exc:
        stop_check(False, f"{section}: the copy of s1.master stopped: {exc}")
        raise Halt(f"{section}: the copy of s1.master stopped (the coordinator's STOP for this stage): {exc}") from None
    path = os.path.join(folder, "TransferCase_E4.xlsx")
    book = Workbook(excel, path, section)
    desk = Desk(path, worker, strip=folder)
    desk.read()
    box = desk.record.gearbox if desk.record is not None else None
    check(turning(desk) and desk.record.digest == desk.reading.digest and under(box.assembly, folder)
          and tuple(box.modes) == KEY["modes"], f"{section}: the copy reads as built from this workbook, its gearbox in "
          f"the copy, with the modes {box and box.modes}")
    desk.say_update()
    u = desk.update
    check(u is not None and not u.needs_new_revision and not u.refusal, f"{section}: the copy classifies as an Update "
          f"with nothing structural: {u and list(u.structural)} {u and u.refusal!r}")
    desk.say_footer(f"{section}, the copy read")
    return folder, path, book, desk, {m: mode_record_frames(desk, m) for m in box.modes}


def moved_frames(frames_by_mode, changes):
    """``frames_by_mode`` (mode -> body -> frame) with each change applied: ``(body, modes or None for every mode, dz
    mm)`` moves that body along Z by dz there (every W8 edit moves a gear along its Z+ shaft, turning nothing)."""
    out = {m: dict(f) for m, f in frames_by_mode.items()}
    for body, modes, dz in changes:
        for mode in out:
            if modes is None or any(swbuild.on_in((x,), mode) for x in modes):
                rotation, at = out[mode][body]
                out[mode][body] = (rotation, (at[0], at[1], at[2] + dz))
    return out


def w8_show(worker, desk, mode, label):
    """``mode`` shown and the train rebuilt (the person picking it in the ConfigurationManager)."""
    def work(s):
        s.show_configuration(mode)
        return bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN)), s.active_configuration()
    got = run(worker, in_assembly(desk.record.gearbox.assembly, work))
    check(got[0] and swbuild.on_in((mode,), got[1]), f"{label}: {mode} shown and rebuilt: {got}")
    return got


def w8_user_turn(worker, desk, label, mode, degrees):
    """The user's turn in ``mode`` (W8-PLAN §5 s2): ``mode`` shown, the input driven ``degrees`` by W5's drive and the
    drive deleted, leaving the train turned there. Every body's turn against §2.3's row for ``mode`` (free ones must
    stand still: a NOTE otherwise). Returns the frames it left, by body, and where §2.3 puts them."""
    box, components, gears, input_gear = drive_inputs(desk)
    say(f"turn    {label}: {input_gear} by {degrees:g}° in {mode} and the drive deleted")
    plane, ruled = drive_assumptions(desk, input_gear, label)
    out = run(worker, drive_job(box.assembly, components, box.layout_component, input_gear, turn_by=degrees,
                                fixed=box.fixed, plane=plane, mode=mode, configs=list(box.modes)))
    say(f"        drive route {out.get('route')!r}; rebuilds {out['rebuilds']}; route reads {out.get('route_reads')}")
    check(not out["errors"] and not out["cleanup"], f"{label}: turned and the drive deleted: {out['errors']} "
          f"{out['cleanup']}")
    frame_none_stop(out["errors"] + out["cleanup"], label)
    stop_check(swbuild.on_in((mode,), out.get("active", "")), f"{label}: {mode} shown for the turn: {out.get('active')}")
    if "after" not in out or "built" not in out or "added" not in out:
        raise Halt(f"{label}: the user's turn left no frames to read: {out['errors']} {out['cleanup']}")
    gap, at = frames_gap(out["built"], mode_record_frames(desk, mode))
    check(gap <= FRAME_TOLERANCE, f"{label}: before the turn every body stands at its frame on record for {mode} "
          f"(largest {gap:.1e} at {at or '-'})")
    turns = {g: turn_degrees(out["built"][g][0], out["after"][g][0]) for g in gears}
    sense = input_sense(label, turns, input_gear, degrees, ruled)
    expected, free = mode_expected(desk, mode, gears, input_gear, degrees, sense)
    say_turns(f"left turned in {mode} (expected from §2.3's key)", turns, expected)
    for g in gears:
        if g not in free:
            stop_check(close_turn(turns[g], expected[g]), f"{label}: {g} left turned {turns[g]}° for "
                       f"{expected[g]:+.9f}°")
        elif turns[g] is None or abs(turns[g]) > DRIVE_TOLERANCE:
            note(f"{label}: {g}, free in {mode}, turned {turns[g]}° with the train")
    want = expected_frames(desk, out["built"], expected)
    gap, at = frames_gap(out["after"], want)
    check(gap <= FRAME_TOLERANCE, f"{label}: every body left where §2.3 puts it, copies carried round (largest "
          f"{gap:.1e} at {at or '-'})")
    check(not any(equations.quote(DRIVE) in t for t in out.get("equations_after", [])) and DRIVE_MATE not in
          [s_[0] for s_ in out.get("states_after", [])], f"{label}: no drive left")
    flags = out.get("flags_after") or {}
    wrong = [(n, c, f) for n, by in flags.items() for c, f in by.items() if f != key_suppressed(n, c)]
    stop_check(bool(flags) and not wrong, f"{label}: after the turn every mate's flag in every configuration is §2.3's: "
               f"wrong {wrong}")
    return out["after"], want, expected


def w8_update(worker, desk, label):
    """Update SolidWorks pressed (``Desk.update_solidworks``) with the SolidWorks calls traced (TRACE): the result's W8
    fields logged, the calls summed by member, every show and put in order, and the elapsed time. Returns (result,
    the calls, seconds)."""
    TRACE["calls"].clear()
    TRACE["on"] = True
    started = time.monotonic()
    try:
        _, result, _ = desk.update_solidworks()
    finally:
        TRACE["on"] = False
    seconds = time.monotonic() - started
    calls = list(TRACE["calls"])
    counts = {}
    for c in calls:
        counts[c[0]] = counts.get(c[0], 0) + 1
    say(f"fact    {label}: the press took {seconds:.1f} s; SolidWorks calls by member {counts}")
    say(f"        shows and puts in order: {[c for c in calls if c[0] in ('ShowConfiguration2', 'put')]}")
    if result is not None:
        say(f"        configuration {result.configuration!r}; visited {result.visited}; put_in {result.put_in}; placed "
            f"{result.placed}; unsuppressed_in {result.unsuppressed_in}; suppressed_in {result.suppressed_in}; slid "
            f"{result.slid}; values_restored {result.values_restored}; extra configurations "
            f"{result.extra_configurations}; extra mates {result.extra_mates}; senses unread {result.senses_unread}; "
            f"positions per configuration {result.positions_per_configuration}; failures {result.failures}")
        for m in result.modes:
            say(f"        post-check of {m.name}: turned {m.turned}; out of step {m.out_of_step}; off axis {m.off_axis}; "
                f"clashes {[(c.gears, round(c.volume, 3)) for c in m.clashes]}; interference error "
                f"{m.interference_error!r}")
    return result, calls, seconds


def puts_by_mode(calls, first):
    """The puts of a traced job, by the configuration shown when each was made (``first``: the one active at the
    start), in order: [(configuration, [Name2, …])], configurations with no put left out."""
    out = [[first, []]]
    for c in calls:
        if c[0] == "ShowConfiguration2":
            out.append([c[1], []])
        elif c[0] == "put":
            out[-1][1].append(c[1])
    return [(m, p) for m, p in out if p]


def nothing_changed_calls(calls):
    """The calls of a traced job that change SolidWorks or show something: none may come before a refusal."""
    return [c for c in calls if c[0] in ("ShowConfiguration2", "SetSuppression2", "SetSystemValue3", "ForceRebuild3",
                                         "EditRebuild3", "put", "AddMate5", "AddConfiguration2", "DeleteConfiguration2")]


def w8_and(items):
    """``2H``, ``2H and N``, ``2H, 4H and N``: the app's own list, written out here so the sentences are the script's."""
    items = [str(i) for i in items]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


PUT_IN = {}       # section -> the configurations its Updates have put in, in order (s2's fresh turn says the state)
SHARED_MAY = ("This version of SolidWorks shows a turn given in one mode in every mode, so the turn may have been given "
              "in another.")


def w8_crossed(desk, mode, turns):
    """The couplings §2.3 engages in ``mode`` whose sleeve and dog stand across each other after ``turns`` (degrees about
    each body's own +Z from the built turn, where every coupling is in step), worked by the script: their turns, the
    dog's taken with the sign its axis has against the sleeve's, differ by other than a whole number of tooth pitches."""
    placed = desk.a.report.layout.placed
    out = []
    for sleeve, dog in key_engaged(mode):
        pitch = 360.0 / float(placed[dog].teeth)
        sign = 1.0 if sum(float(a) * float(b) for a, b in zip(placed[sleeve].axis, placed[dog].axis)) > 0 else -1.0
        d = (turns.get(sleeve, 0.0) - sign * turns.get(dog, 0.0)) % pitch
        if min(d, pitch - d) > 1e-6:
            out.append((sleeve, dog))
    return out


W8_TURN_CLASH = {"4L": [("LoDog", "RangeSlv")]}   # the stage 2c ruling: on False, 4L's LoDog across RangeSlv, alone


def w8_shown_turned(worker, desk, label, mode, turns, positions):
    """After the user's turn in 2H, ``mode`` shown and read through handles fetched after the show (W8-PLAN §5 s2 as the
    running version answers, ``swcom.positions_per_configuration``). False: every body turned as in 2H (``turns``, the
    key's ratio × the turn, to 1e-6; the front train still), standing where those turns put it from the mode's own
    frames on record (copies carried round), and only W8_TURN_CLASH's pair interfering, its volume logged. True: the
    plan's reading, the mode as built (``measure_mode``). None: the frames and clashes logged as facts, nothing
    asserted about a turn."""
    box = desk.record.gearbox
    if positions is True:
        return measure_mode(worker, desk, f"{label}: as built", mode)
    out = run(worker, mode_state_job(box, mode))
    stop_check(swbuild.on_in((mode,), out["active"]), f"{label}: {mode} shown, the active configuration reads "
               f"{out['active']}")
    check(out["rebuilt"], f"{label}: the train's rebuild in {mode} answered True")
    record = mode_record_frames(desk, mode)
    got = {g: turn_degrees(record[g][0], out["frames"][g][0]) for g in turns}
    say_turns(f"{label}: each body's turn in {mode} from its frame on record there (expected: 2H's)", got, turns)
    merged = swbuild._clashes(out["clashes"], {n: g for g, n in bodies(box)})  # noqa: SLF001
    clashes = [(tuple(sorted(c.gears)), round(c.volume, 3)) for c in merged]
    say(f"fact    {label}: interference in {mode}: {clashes or 'none'}")
    if positions is None:
        say_off(label, mode, out["frames"], record)
        return out
    for g in turns:
        stop_check(close_turn(got[g], turns[g]), f"{label}: in {mode}, {g} stands turned {got[g]}° from its frame on "
                   f"record, the turn given in 2H ({turns[g]:+.9f}°)")
    want = expected_frames(desk, record, turns)
    gap, at = frames_gap(out["frames"], want)
    if not stop_check(gap <= FRAME_TOLERANCE, f"{label}: in {mode} every body stands where 2H's turn puts it from "
                      f"{mode}'s frames on record, copies carried round (largest {gap:.1e} at {at or '-'})"):
        say_off(label, mode, out["frames"], want)
    expected = W8_TURN_CLASH.get(mode, [])
    check(sorted(p for p, _ in clashes) == expected, f"{label}: the interference in {mode} is "
          f"{'exactly ' + str(expected) + ', expected there' if expected else 'none'}: {clashes}")
    return out


def w8_read_all(worker, desk, label, wanted, last):
    """Every mode shown in turn (``last`` last, so it is left active) and every body's frame read through handles fetched
    after the show, judged against ``wanted`` (mode -> body -> frame) to 1e-6; each body off logged with its turn and
    how far its origin stands. The coordinator's correction (stage 2c): where a body stands is read from its frame,
    never from ``ModeCheck.turned``. Returns the frames by mode."""
    box = desk.record.gearbox
    order = [m for m in box.modes if not swbuild.on_in((m,), last)] + [last]
    out = {}
    for mode in order:
        got = run(worker, mode_state_job(box, mode, full=False))
        stop_check(swbuild.on_in((mode,), got["active"]), f"{label}: {mode} shown: {got['active']}")
        gap, at = frames_gap(got["frames"], wanted[mode])
        if not check(gap <= FRAME_TOLERANCE, f"{label}: read through fresh handles, every body in {mode} where it "
                     f"should stand (largest {gap:.1e} at {at or '-'})"):
            say_off(label, mode, got["frames"], wanted[mode])
        out[mode] = got["frames"]
    return out


def w8_press_after_turn(worker, desk, label, mode, positions, turns, folder, presses, expect="finding"):
    """Update SolidWorks pressed with ``mode`` showing after the user's turn in 2H, nothing changed in the workbook.
    ``expect`` "finding": what the running version's answer says — False (the turn shows here), ``mode``'s
    couplings found across and, the quiet path having something to put, every mode put whole to the built frames,
    the active one last (the app fix a87c1c5, the coordinator's stage 2d); True, the plan's quiet press, nothing put
    or shown. ``expect`` None: judged by what the press reports (a put: the checks below; none: the quiet ones).

    A press that puts: no failure; ``put_in`` every mode, ``mode`` last; every mode shown, ``mode`` last and left
    active; every per-mode flag read in every configuration after the last put; ``mode``'s couplings found across
    when judged, and only couplings; the status's parts that do not depend on the turn finding asserted (the
    re-placed list "in every mode", each crossed pair said once, "the gears of 4L are back …", the "It worked in …
    showed and checked …" sentence) and the whole logged; the assembly marked; every body at its built frame in every
    mode afterwards, read through fresh handles."""
    box = desk.record.gearbox
    save_assembly(worker, desk, f"{label}: {mode} active, so the marks after the press are its own")
    desk.plan_solidworks()
    desk.say_update()
    frames_before, flags_before = gear_frames(worker, desk), gearbox_flags(worker, desk)
    guard()
    result, calls, seconds = w8_update(worker, desk, label)
    presses.append((label, seconds))
    if result is None:
        check(False, f"{label}: refused: {desk.note[0]!r}")
        return None
    PUT_IN.setdefault(label.split()[0], []).extend(result.put_in)
    said = desk.note[0] if desk.note else ""
    say(f"        the status verbatim: {said!r}")
    others = [m for m in box.modes if not swbuild.on_in((m,), mode)]
    shows = [c[1] for c in calls if c[0] == "ShowConfiguration2"]
    by_mode = puts_by_mode(calls, mode)
    say(f"fact    {label}: shows in order {shows}; puts by the configuration shown "
        f"{[(m, len(n), n[:1]) for m, n in by_mode]}; put_in {result.put_in}")
    if expect == "finding" and positions is True:
        check(not result.put_in, f"{label}: a turn stays in its mode on this version, so {mode} stands as built and "
              f"nothing is put: put_in {result.put_in}")
    elif expect == "finding" and positions is False:
        check(bool(result.put_in), f"{label}: this version shows the turn in every mode, so {mode}'s couplings are "
              f"found across and the press puts: put_in {result.put_in}")
    else:
        say(f"fact    {label}: judged by what the press reports (put_in {result.put_in})")
    if not result.put_in:
        check(result.ok and swbuild.on_in((mode,), result.configuration) and not result.visited and not result.placed
              and not result.changed and not result.modes and not result.senses_unread and not result.turned,
              f"{label}: nothing put, shown or changed, every sense read, the train in step in {mode}")
        check(not nothing_changed_calls(calls), f"{label}: no show, flag, value, rebuild or put: "
              f"{nothing_changed_calls(calls)}")
        check_quiet_update(worker, desk, result, label, frames_before, flags_before)
        quiet = f"It worked in {mode}, the configuration that was active; it did not show the other modes"
        check(quiet in said, f"{label}: the status says {quiet!r}")
        say(f"fact    {label}: the sentence on a turn shown in every mode is "
            f"{'said' if ui_text.TURN_SHOWN_ELSEWHERE in said else 'not said'}")
        return result
    check(result.ok and not result.failures and swbuild.on_in((mode,), result.configuration),
          f"{label}: no failure, worked in {mode}: {result.failures}")
    check(set(result.put_in) == set(box.modes) and swbuild.on_in((mode,), result.put_in[-1]),
          f"{label}: every mode put, {mode} last: put_in {result.put_in}")
    check(result.visited == others and [c.name for c in result.modes] == others + [mode],
          f"{label}: every other mode visited: visited {result.visited}, checks {[c.name for c in result.modes]}")
    check(shows == others + [mode], f"{label}: every mode shown, {mode} last: {shows}")
    active = run(worker, in_assembly(box.assembly, lambda s: s.active_configuration()))
    check(swbuild.on_in((mode,), active), f"{label}: {mode} left active: {active}")
    put_at = [i for i, c in enumerate(calls) if c[0] == "put"]
    show_at = [i for i, c in enumerate(calls) if c[0] == "ShowConfiguration2"]
    per_mode = [m.name for m in box.mates if m.modes]
    after_put = calls[put_at[-1] + 1:] if put_at else calls
    missing = [(n, c) for n in per_mode for c in box.modes if ("IsSuppressed2", n, 3, [c]) not in after_put]
    check(per_mode and not missing, f"{label}: after the last put every per-mode mate's flag read in every "
          f"configuration, one IsSuppressed2(3, [c]) each ({len(per_mode)} mates): missing {missing}")
    after_show = calls[show_at[-1] + 1:] if show_at else []
    late = [(n, c) for n in per_mode for c in box.modes if ("IsSuppressed2", n, 3, [c]) in after_show]
    say(f"fact    {label}: of those reads, {len(late)} of {len(per_mode) * len(box.modes)} come after the last show")
    here = result.modes[-1]
    couplings = {frozenset(p) for p in key_engaged(mode)}
    check(here.out_of_step and all(frozenset(p) in couplings for p in here.out_of_step),
          f"{label}: {mode}'s coupling(s) found out of step there and nothing else: {here.out_of_step}")
    if expect == "finding" and positions is False:
        want = w8_crossed(desk, mode, turns)
        check({frozenset(p) for p in here.out_of_step} == {frozenset(p) for p in want},
              f"{label}: the couplings found across are those 2H's turn crosses in {mode}, worked by the script: {want}")
    for c in result.modes:
        # ModeCheck.turned is unjudged while any body of the train is off its place: logged, never asserted.
        say(f"fact    {label}: {c.name} when shown: out of step {c.out_of_step}, off axis {c.off_axis}, turned "
            f"{c.turned}; after its put: clashes {[(x.gears, round(x.volume, 3)) for x in c.clashes]}")
    check(all(not c.clashes and not c.interference_error for c in result.modes) and not result.senses_unread,
          f"{label}: no interference in any mode after its put, every sense read: senses unread {result.senses_unread}")
    couplings_all = {frozenset(k) for m in box.modes for k in key_engaged(m)}
    check(all(frozenset(p) in couplings_all for p in result.out_of_step), f"{label}: only couplings found out of step "
          f"before the Update: {result.out_of_step}")
    placed = ("Updated SolidWorks: re-placed Carrier (the carrier), Sun, Pl (3 copies), InDog, LoDog, RangeSlv, FrontDog, "
              "ModeSlv, FDrive, FIdler and FOut in every mode")
    check(placed in said, f"{label}: the status says {placed!r}")
    crossed = [(a, b) for a, b in here.out_of_step]
    for a, b in crossed:
        across = f"In {mode}, {a}'s teeth stood across {b}'s"
        check(said.count(across) == 1, f"{label}: the status says {across!r} once")
    back = f"the gears of {mode} are back at the turn they were built at."
    worked = (f"It worked in {mode}, the configuration that was active, then showed and checked {w8_and(others)} and "
              f"left the assembly in {mode}.")
    for text in (back, worked):
        check(text in said, f"{label}: the status says {text!r}")
    check("did not show the other modes" not in said, f"{label}: and not the quiet press's sentence")
    say(f"fact    {label}: the turn finding's sentence ({SHARED_MAY!r}) is {'said' if SHARED_MAY in said else 'not said'}")
    check(any(os.path.basename(str(p)).lower() == os.path.basename(box.assembly).lower() for p in result.changed),
          f"{label}: the assembly is among the documents changed: {result.changed}")
    update_marks(worker, desk, result, label, folder)
    w8_read_all(worker, desk, f"{label}, every mode read after the press", {m: mode_record_frames(desk, m)
                                                                             for m in box.modes}, mode)
    return result


def w8_press_in_step(worker, desk, label, mode, positions, presses):
    """Update SolidWorks pressed with ``mode`` showing, its train turned and in step there, nothing changed in the
    workbook (stage 2c's new step): nothing put, nothing shown; the status says the gears stand where they were turned
    and, only where the version shows a turn in every mode (False), ``ui_text.TURN_SHOWN_ELSEWHERE`` exactly."""
    box = desk.record.gearbox
    save_assembly(worker, desk, f"{label}: {mode} active, so the marks after the press are its own")
    desk.plan_solidworks()
    desk.say_update()
    frames_before, flags_before = gear_frames(worker, desk), gearbox_flags(worker, desk)
    guard()
    result, calls, seconds = w8_update(worker, desk, label)
    presses.append((label, seconds))
    if result is None:
        check(False, f"{label}: refused: {desk.note[0]!r}")
        return None
    said = desk.note[0] if desk.note else ""
    say(f"        the status verbatim: {said!r}")
    check(result.ok and swbuild.on_in((mode,), result.configuration) and not result.put_in and not result.visited
          and not result.placed and not result.modes and not result.out_of_step and result.turned
          and result.positions_per_configuration == positions,
          f"{label}: the train found turned and in step in {mode}: nothing put, nothing shown (put_in {result.put_in}, "
          f"visited {result.visited}, placed {result.placed}, out of step {result.out_of_step}, turned {result.turned})")
    check(not nothing_changed_calls(calls), f"{label}: no show, flag, value, rebuild or put: "
          f"{nothing_changed_calls(calls)}")
    check_quiet_update(worker, desk, result, label, frames_before, flags_before)
    stand = "The gears stand where they were turned in SolidWorks."
    quiet = f"It worked in {mode}, the configuration that was active; it did not show the other modes"
    check(stand in said and quiet in said, f"{label}: the status says {stand!r} and {quiet!r}")
    if positions is False:
        check(f"{stand} {ui_text.TURN_SHOWN_ELSEWHERE}" in said, f"{label}: on this version, straight after it, "
              f"exactly {ui_text.TURN_SHOWN_ELSEWHERE!r}")
    else:
        check(ui_text.TURN_SHOWN_ELSEWHERE not in said and "shows that turn in every mode" not in said,
              f"{label}: the version's answer is {positions}, so the status does not carry the sentence on a turn shown "
              "in every mode")
    return result


def section_s2(worker, excel):
    say("== s2  turning and switching (W8-PLAN §5, as the running version answers swcom.positions_per_configuration), "
        "a copy of s1.master: the user's turn in 2H; 4H, N and 4L shown (False: each at the same turn, 4L's LoDog "
        "across RangeSlv; True: each as built); 2H at the turn; Update in 4L (False: every mode put whole to the built "
        "frames, 4L last; True: quiet); a fresh turn in 2H, Update in 2H (nothing put or shown); 4L shown and read (a "
        "fact); Update in 4L (judged by what it reports); "
        "FDrive, FIdler, FOut At 130 -> 132 -> Update: every mode put, the active one last; raw flags straight after; "
        "every mode measured; the drive in 4H and 4L")
    folder, path, book, desk, built = start_w8_copy(worker, excel, "s2")
    box = desk.record.gearbox
    positions = swcom.positions_per_configuration(TAG["revision"])
    reading = {True: "a turn stays in its mode (the plan's reading)", False: "a turn shows in every mode",
               None: "unsettled: nothing is asserted about a turn in the other modes"}[positions]
    say(f"fact    s2: swcom.positions_per_configuration({TAG['revision']}) is {positions}: {reading}")
    presses = []
    _, turned, turns = w8_user_turn(worker, desk, "s2 the user's turn in 2H", "2H", 37.0)
    for mode in ("4H", "N", "4L"):
        guard()
        w8_shown_turned(worker, desk, f"s2, 2H turned, {mode} shown", mode, turns, positions)
    out = run(worker, mode_state_job(box, "2H"))
    stop_check(swbuild.on_in(("2H",), out["active"]), f"s2: 2H shown again: {out['active']}")
    gap, at = frames_gap(out["frames"], turned)
    stop_check(gap <= FRAME_TOLERANCE, f"s2: 2H shown again stands at the 37° turn, every body (largest {gap:.1e} at "
               f"{at or '-'})")
    merged = swbuild._clashes(out["clashes"], {n: g for g, n in bodies(box)})  # noqa: SLF001
    stop_check(not merged, f"s2: 2H at the turn, no interference: {[(c.gears, round(c.volume, 3)) for c in merged]}")
    # An Update in 4L, nothing changed in the workbook.
    w8_show(worker, desk, "4L", "s2")
    w8_press_after_turn(worker, desk, "s2 quiet Update in 4L", "4L", positions, turns, folder, presses)
    desk.say_footer("s2, after the quiet press in 4L")
    # Stage 2c's new step: the train turned in 2H, in step there; Update in 2H; 4L shown and read; Update in 4L.
    say("-- s2: the train turned in 2H (in step there) -> Update in 2H; then 4L shown, LoDog read across RangeSlv -> "
        "Update in 4L")
    put_before = sorted({m for m in box.modes if any(swbuild.on_in((m,), p) for p in PUT_IN.get("s2", ()))})
    say(f"fact    s2: the state before the fresh turn: modes put in by an Update so far {put_before or 'none'}; "
        "every mode read at its built frames after the last press (above)")
    w8_show(worker, desk, "2H", "s2")
    _, _, turns2 = w8_user_turn(worker, desk, "s2 the fresh turn in 2H", "2H", 37.0)
    w8_press_in_step(worker, desk, "s2 Update in 2H, the train turned and in step there", "2H", positions, presses)
    desk.say_footer("s2, after the press in 2H")
    guard()
    w8_shown_turned(worker, desk, "s2, the fresh turn in 2H, 4L shown (a fact until s7 settles it)", "4L", turns2,
                    None)
    w8_press_after_turn(worker, desk, "s2 Update in 4L after the fresh turn in 2H", "4L", positions, turns2, folder,
                        presses, expect=None)
    desk.say_footer("s2, after the second press in 4L")
    # The changed Update.
    expected = moved_frames(built, [(g, None, 2.0) for g in ("FDrive", "FIdler", "FOut")])
    say("-- s2: Excel FDrive, FIdler and FOut At 130 -> 132, 4L active -> Update")
    edit(desk, book, *[("Gears", cell(book, "Gears", "At", g), 132) for g in ("FDrive", "FIdler", "FOut")])
    u = desk.update
    check(u is not None and not u.needs_new_revision and not u.refusal, f"s2: the move is an Update: structural "
          f"{u and list(u.structural)}, refusal {u and u.refusal!r}")
    desk.say_footer("s2, after the edit")
    guard()
    result, calls, seconds = w8_update(worker, desk, "s2 changed Update")
    presses.append(("s2 changed Update", seconds))
    box = desk.record.gearbox
    raw_flag_reads(worker, desk, "s2 straight after the changed Update", names=[m.name for m in box.mates])
    if result is None:
        check(False, f"s2 changed Update: refused: {desk.note[0]!r}")
        say(f"fact    s2: the presses took {[(n, round(t, 1)) for n, t in presses]} s")
        end_copy(worker, folder, "s2")
        return
    order = ["2H", "4H", "N"]
    check(result.ok and not result.failures, f"s2 changed Update: no failure: {result.failures}")
    check(result.put_in == order + ["4L"] and result.visited == order and [m.name for m in result.modes] == order + ["4L"],
          f"s2 changed Update: every mode shown and put, 4L last: put_in {result.put_in}, visited {result.visited}")
    # Where each mode stood before this press was read from frames after the last press in 4L (w8_read_all);
    # ModeCheck.turned is unjudged while a body of the train is off its place, so it is logged only.
    say(f"fact    s2 changed Update: each mode's judgement when shown (turned is unjudged with a body off its place): "
        f"{[(m.name, m.turned, m.off_axis, m.out_of_step) for m in result.modes]}")
    check(all(not m.clashes and not m.interference_error for m in result.modes) and not result.senses_unread,
          "s2 changed Update: no interference in any mode's post-check, every sense read")
    carrier = next(c.component for c in carriers_of(box))
    by_mode = puts_by_mode(calls, "4L")
    for mode, names in by_mode:
        say(f"fact    s2 changed Update: puts in {mode}, in order: {names}")
    check([m for m, _ in by_mode] == order + ["4L"] and all(names and names[0] == carrier for _, names in by_mode),
          f"s2 changed Update: in every mode the train is put, the carrier ({carrier}) first")
    update_marks(worker, desk, result, "s2 changed Update", folder)
    values = run(worker, lambda s: live_globals(s, box.assembly))
    want = {"FIdler Face Z": 127.0, "FOut Face Z": 127.0, "FrontDog Face Z": 107.0}
    check(all(abs(float(values.get(k, float("nan"))) - v) <= 1e-9 for k, v in want.items()),
          f"s2 changed Update: the assembly's globals {({k: values.get(k) for k in want})}, the edit's {want}")
    say(f"        the sentence: {desk.note[0]!r}")
    check(all(re.search(rf"\b{m}\b", desk.note[0]) for m in order), f"s2 changed Update: the sentence names every "
          f"mode shown ({order})")
    say(f"fact    s2: the presses took {[(n, round(t, 1)) for n, t in presses]} s")
    measure_modes(worker, desk, "s2 after the changed Update", controls=True, active="4L", expected=expected)
    for mode in ("4H", "4L"):
        guard()
        mode_drive_proof(worker, desk, f"s2 after the changed Update, driven in {mode}", mode)
    end_copy(worker, folder, "s2")


def w8_m2_press(worker, desk, label, name, modes_on):
    """W8-INTERFACES' M2 (d2f492e): a mate the record does not know, on in ``modes_on`` → the Update refuses, naming it and
    the modes, before showing or changing anything: the sentence; between the open and the refusal no show, flag, value,
    rebuild, put or mate made; the mate read one ``IsSuppressed2(3, [c])`` per mode, in mode order; the active
    configuration, every document's save flag and every frame as before; no window under the watch."""
    box = desk.record.gearbox
    save_assembly(worker, desk, f"{label}: so the marks after the refused press are its own")
    desk.plan_solidworks()
    frames_before, flags_before = gear_frames(worker, desk), gearbox_flags(worker, desk)
    active_before = run(worker, in_assembly(box.assembly, lambda s: s.active_configuration()))
    windows = WINDOWS["count"]
    guard()
    result, calls, _ = w8_update(worker, desk, label)
    modes = list(box.modes)
    listed = modes_on[0] if len(modes_on) == 1 else ", ".join(modes_on[:-1]) + f" and {modes_on[-1]}"
    lead = (f"In mode{'s' if len(modes_on) > 1 else ''} {listed}, {name} is a mate in {os.path.basename(box.assembly)} "
            "that Gear Generator did not make, and it may hold the gears where Update SolidWorks would put them, so "
            "nothing is changed;")
    whole = lead + f" in SolidWorks, suppress {name} in {listed} and press Update SolidWorks again."
    said = desk.note[0] if desk.note else ""
    say(f"        the refusal: {said!r}")
    check(result is None and desk.error is not None and (whole in said if len(modes_on) == 1 else lead in said),
          f"{label}: Update refuses naming {name} and {listed}" + (" verbatim" if len(modes_on) == 1 else ""))
    check(not nothing_changed_calls(calls), f"{label}: between the open and the refusal no show, flag, value, rebuild, "
          f"put or mate made: {nothing_changed_calls(calls)}")
    reads = [c[3] for c in calls if c[0] == "IsSuppressed2" and c[1] == name and c[2] == 3]
    check(reads == [[m] for m in modes], f"{label}: {name} found by its name and read one IsSuppressed2(3, [c]) per "
          f"mode, in mode order: {reads}")
    active_after = run(worker, in_assembly(box.assembly, lambda s: s.active_configuration()))
    gap, at = frames_gap(gear_frames(worker, desk), frames_before)
    flags_after = gearbox_flags(worker, desk)
    check(active_after == active_before and gap <= FRAME_TOLERANCE and not marked(flags_before)
          and not marked(flags_after) and WINDOWS["count"] == windows,
          f"{label}: nothing changed: {active_before} still active ({active_after}), every frame where it stood "
          f"(largest {gap:.1e} at {at or '-'}), nothing marked (before {marked(flags_before)}, after "
          f"{marked(flags_after)}), no window under the watch ({WINDOWS['count'] - windows} new)")


def w8_flags(worker, desk, name, suppress=None, configurations=()):
    """The mate ``name``'s flag in every mode, after (given ``suppress``) setting it in ``configurations`` with the
    per-configuration call; the active configuration too."""
    box = desk.record.gearbox

    def work(s):
        s.find_mate("uf", name)
        if suppress is not None and configurations:
            s.set_mate_suppressed_in("uf", suppress, list(configurations))
        return s.mate_suppression("uf", list(box.modes)), s.active_configuration()
    return run(worker, in_assembly(box.assembly, work))


def w8_unknown_mate(worker, desk, label):
    """W8-PLAN §5 s3 with W8-REVIEW-FIX-TIER11's M2: an angle mate the record does not know, made with 2H active on the
    input Sun (built at θ = 0, so a 90° angle mate holds it where it stands), then: on in every mode → refused "In modes
    2H, 4H, N and 4L"; on in N only → refused "In mode N", nothing shown or changed; suppressed in every mode → listed
    and left; ``Exploded`` added → listed and left; the mate on in N again with Exploded active → J13's refusal, the mate
    never read; 2H shown, the mate suppressed again."""
    box = desk.record.gearbox
    sun = next(n for g, n in bodies(box) if g == box.drag[0])

    def add(s):
        s.find_component("u1", sun)
        s.find_component("ulay", box.layout_component)
        before = s.component_frame("u1")
        name, _ = s.add_mate("user", "angle", "u1:plane2", "ulay:plane3", DRIVE_FROM)
        rebuilt = bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN))
        return name, s.mate_status(name), rebuilt, frame_gap(before, s.component_frame("u1")), s.active_configuration()
    name, status, rebuilt, moved, active = run(worker, in_assembly(box.assembly, add))
    say(f"        made {name!r} (SolidWorks' own name) on {box.drag[0]} with {active} active: AddMate5 status {status}, "
        f"rebuilt {rebuilt}, {box.drag[0]} moved {moved:.1e}")
    check(moved <= FRAME_TOLERANCE and swbuild.on_in(("2H",), active), f"{label}: the angle mate made with 2H active "
          f"moved nothing")
    flags, _ = w8_flags(worker, desk, name)
    say(f"fact    {label}: {name} as made reads {flags} (suppressed True) in each mode")
    off = [m for m, f in flags.items() if f]
    if off:
        flags, _ = w8_flags(worker, desk, name, False, off)
    check(not any(flags.values()), f"{label}: {name} on in every mode: {flags}")
    w8_m2_press(worker, desk, f"{label}, on in every mode", name, list(box.modes))
    flags, active = w8_flags(worker, desk, name, True, ["2H", "4H", "4L"])
    check(flags == {"2H": True, "4H": True, "N": False, "4L": True} and swbuild.on_in(("2H",), active),
          f"{label}: {name} suppressed in 2H, 4H and 4L with 2H active, read back one name per call: {flags}, active "
          f"{active}")
    w8_m2_press(worker, desk, f"{label}, on in N only", name, ["N"])
    # Suppressed in N too -> listed and left.
    flags, active = w8_flags(worker, desk, name, True, ["N"])
    check(all(flags.values()) and swbuild.on_in(("2H",), active), f"{label}: {name} suppressed in N, 2H active: {flags}")
    listed_and_left(worker, desk, f"{label}, suppressed in every mode", name)
    flags_after, _ = w8_flags(worker, desk, name)
    check(flags_after == flags, f"{label}: {name}'s four flags unchanged by the Update: {flags_after}")
    # Exploded: added (listed and left), then active (J13), the mate on in N meanwhile.

    def add_exploded(s):
        s.add_configuration("Exploded")
        made_active = s.active_configuration()
        s.show_configuration("2H")
        rebuilt = bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN))
        return made_active, rebuilt, s.active_configuration(), s.configurations()
    got = run(worker, in_assembly(box.assembly, add_exploded))
    say(f"        Exploded added by the script (active {got[0]}), 2H shown again: rebuilt {got[1]}, active {got[2]}, "
        f"configurations {got[3]}")
    result = listed_and_left(worker, desk, f"{label}, Exploded added", None)
    check(result is not None and result.extra_configurations == ["Exploded"], f"{label}: Exploded listed and left: "
          f"{result and result.extra_configurations}")
    flags, active = w8_flags(worker, desk, name, False, ["N"])
    check(flags["N"] is False and swbuild.on_in(("2H",), active), f"{label}: {name} on in N again, 2H active: {flags}")
    w8_show(worker, desk, "Exploded", label)
    save_assembly(worker, desk, f"{label}: Exploded active, so the marks after the refused press are its own")
    desk.plan_solidworks()
    flags_before, frames_before = gearbox_flags(worker, desk), gear_frames(worker, desk)
    result, calls, _ = w8_update(worker, desk, f"{label}, Exploded active")
    j13 = ("Update SolidWorks works in one of the gearbox's own configurations (2H, 4H, N and 4L), and Exploded is "
           "active in SolidWorks: pick one of them and press Update SolidWorks again.")
    said = desk.note[0] if desk.note else ""
    say(f"        the refusal: {said!r}")
    check(result is None and j13 in said, f"{label}: with Exploded active the refusal is J13's, not M2's")
    reads = [c for c in calls if c[0] == "IsSuppressed2" and c[1] == name and c[2] == 3]
    check(not reads and not nothing_changed_calls(calls), f"{label}: with Exploded active {name} is never read and "
          f"nothing changes: reads {reads}, changes {nothing_changed_calls(calls)}")
    gap, at = frames_gap(gear_frames(worker, desk), frames_before)
    flags_after = gearbox_flags(worker, desk)
    check(gap <= FRAME_TOLERANCE and not marked(flags_before) and not marked(flags_after),
          f"{label}: Exploded's refusal changed nothing (largest {gap:.1e}; marked after {marked(flags_after)})")
    w8_show(worker, desk, "2H", label)
    flags, _ = w8_flags(worker, desk, name, True, ["N"])
    check(all(flags.values()), f"{label}: {name} suppressed in N again: {flags}")


def listed_and_left(worker, desk, label, name):
    """A press that must go through, quiet, listing ``name`` (a mate the record does not know, suppressed in every mode)
    as left alone in its CHECK line and the footer, both logged verbatim (their wording is changing; the name is what is
    held). Returns the result."""
    save_assembly(worker, desk, f"{label}: so the marks after the press are its own")
    desk.plan_solidworks()
    frames_before, flags_before = gear_frames(worker, desk), gearbox_flags(worker, desk)
    guard()
    result, calls, _ = w8_update(worker, desk, label)
    if result is None:
        check(False, f"{label}: Update refused: {desk.note[0]!r}")
        return None
    lines = result.log_lines()
    for line in lines:
        if line.startswith("CHECK") or (name and name in line):
            say(f"        the result's line: {line}")
    f = desk.say_footer(f"{label}, after the press")
    check(result.ok, f"{label}: Update goes through: {result.failures}")
    if name:
        check(name in result.extra_mates and any(name in line for line in lines) and name in f.text,
              f"{label}: {name} listed and left, named in the result's lines and the footer: extra mates "
              f"{result.extra_mates}")
    check(not nothing_changed_calls(calls), f"{label}: a quiet press: no show, flag, value, rebuild or put: "
          f"{nothing_changed_calls(calls)}")
    check_quiet_update(worker, desk, result, label, frames_before, flags_before)
    return result


def section_s3(worker, excel):
    say("== s3  D10 per configuration and the refusals (W8-PLAN §5, with W8-REVIEW-FIX-TIER11's M2), a copy of "
        "s1.master, 2H active: two flags in 4L and N's slide value changed by the script -> Update puts them right; "
        "an angle mate the record does not know -> refused in every mode, then in N only, then listed and left; "
        "Exploded added, then active (J13); 4H deleted -> Build again…")
    folder, path, book, desk, built = start_w8_copy(worker, excel, "s3")
    box = desk.record.gearbox

    def tamper(s):
        out = {}
        for handle, (name, suppress, where) in enumerate((("RangeSlv engages LoDog", True, "4L"),
                                                           ("RangeSlv engages InDog", False, "4L"))):
            s.find_mate(f"t{handle}", name)
            s.set_mate_suppressed_in(f"t{handle}", suppress, [where])
            out[name] = s.mate_suppression(f"t{handle}", list(box.modes))
        s.find_mate("tv", "RangeSlv along Rear")
        s.set_dimension_in("tv", 58.0, ["N"])
        out["RangeSlv along Rear"] = s.dimension_values("tv", list(box.modes))
        return s.active_configuration(), out
    active, out = run(worker, in_assembly(box.assembly, tamper))
    say(f"        changed by the script with {active} active: {out}")
    check(swbuild.on_in(("2H",), active) and out["RangeSlv engages LoDog"]["4L"] is True
          and out["RangeSlv engages InDog"]["4L"] is False and abs(out["RangeSlv along Rear"]["N"] - 58.0) <= 1e-6,
          "s3: in 4L RangeSlv engages LoDog suppressed and RangeSlv engages InDog on, N's RangeSlv along Rear 58 mm, "
          "2H active, nothing shown")
    save_assembly(worker, desk, "s3: after the script's changes, so the marks after the Update are its own")
    desk.plan_solidworks()
    desk.say_update()
    guard()
    result, calls, _ = w8_update(worker, desk, "s3 D10 Update in 2H")
    if result is not None:
        check(result.ok and swbuild.on_in(("2H",), result.configuration)
              and result.unsuppressed_in == [("RangeSlv engages LoDog", "4L")]
              and result.suppressed_in == [("RangeSlv engages InDog", "4L")]
              and result.values_restored == [("RangeSlv along Rear", "N")] and not result.slid,
              "s3 D10 Update: the two flags in 4L and N's value put right, nothing else")
        shows = [i for i, c in enumerate(calls) if c[0] == "ShowConfiguration2"]
        sets = [i for i, c in enumerate(calls) if c[0] in ("SetSuppression2", "SetSystemValue3")]
        check(bool(sets) and (not shows or max(sets) < shows[0]), f"s3 D10 Update: every flag and value set before "
              f"anything is shown (sets at {sets}, first show at {shows[:1]})")
        check(result.visited == ["4H", "N", "4L"] and [m.name for m in result.modes] == ["4H", "N", "4L", "2H"],
              f"s3 D10 Update: having changed something, it shows and checks every mode: visited {result.visited}")
        say(f"        the sentence: {desk.note[0]!r}")
        update_marks(worker, desk, result, "s3 D10 Update", folder)
    else:
        check(False, f"s3 D10 Update: refused: {desk.note[0]!r}")
    raw_flag_reads(worker, desk, "s3 after D10", names=[m.name for m in box.mates])
    measure_modes(worker, desk, "s3 after D10", controls=True, active="2H", expected=built)
    w8_show(worker, desk, "2H", "s3")
    w8_unknown_mate(worker, desk, "s3 M2")
    # 4H deleted -> NotAsBuilt, Build again… offered.
    got = run(worker, in_assembly(box.assembly, lambda s: (s.delete_configuration("4H"), s.configurations(),
                                                         s.active_configuration())[1:]))
    say(f"        4H deleted by the script: configurations {got[0]}, active {got[1]}")
    save_assembly(worker, desk, "s3: 4H deleted")
    desk.plan_solidworks()
    result, calls, _ = w8_update(worker, desk, "s3 with 4H deleted")
    said = desk.note[0] if desk.note else ""
    say(f"        the refusal: {said!r}; raised {type(desk.error).__name__ if desk.error else None}")
    gone = f"The configuration 4H is not in {os.path.basename(box.assembly)} any more: it was renamed or deleted in SolidWorks."
    check(result is None and isinstance(desk.error, (swcom.ComponentGone, swbuild.NotAsBuilt)) and gone in said,
          "s3: with 4H deleted the Update says so and changes nothing")
    check(not nothing_changed_calls(calls), f"s3 with 4H deleted: nothing changed: {nothing_changed_calls(calls)}")
    f = desk.say_footer("s3, 4H deleted")
    check(f.build_enabled, f"s3: Build again… offered ({f.build_label!r})")
    end_copy(worker, folder, "s3")


def section_s4(worker, excel):
    say("== s4  the edits Update carries, then a structural one (W8-PLAN §5), a copy of s1.master, 2H active throughout "
        "the edits: RangeSlv L=+10.5; ModeSlv At 101 with 4WD=+9; 4H's ModeSlv 4WD -> 2WD (J14); then a Modes row 4X "
        "-> Build again… -> _r2 with five configurations")
    folder, path, book, desk, built = start_w8_copy(worker, excel, "s4")
    expect = built
    rng, mod = "RangeSlv along Rear", "ModeSlv along Rear"

    def press(label, cells, key_edit, changes, slid, flags=None, drive=None):
        nonlocal expect
        say(f"-- {label}: Excel {[(c[0] + '!' + c[1], c[2]) for c in cells]} -> Update, 2H active")
        edit(desk, book, *cells)
        key_edit()
        expect = moved_frames(expect, changes)
        u = desk.update
        check(u is not None and not u.needs_new_revision and not u.refusal, f"{label}: an Update: structural "
              f"{u and list(u.structural)}, refusal {u and u.refusal!r}")
        desk.say_footer(f"{label}, after the edit")
        guard()
        result, calls, _ = w8_update(worker, desk, label)
        box = desk.record.gearbox
        if result is None:
            check(False, f"{label}: refused: {desk.note[0]!r}")
            return
        check(result.ok and swbuild.on_in(("2H",), result.configuration) and sorted(result.slid) == sorted(slid),
              f"{label}: the slide values set with 2H active are the edit's: slid {result.slid}, want {slid}")
        sets = sorted((round(float(c[1]), 9), tuple(c[2] or ())) for c in calls if c[0] == "SetSystemValue3")
        shows = [i for i, c in enumerate(calls) if c[0] == "ShowConfiguration2"]
        first_set = next((i for i, c in enumerate(calls) if c[0] == "SetSystemValue3"), None)
        check(sets == sorted((round(v / 1000.0, 9), (c,)) for _, c, v in slid),
              f"{label}: one SetSystemValue3 per value set, each naming only its configuration: {sets}")
        check(first_set is not None and (not shows or first_set < shows[0]), f"{label}: the values set before anything "
              "is shown (while 2H is active)")
        if flags is not None:
            check(sorted(result.suppressed_in) == sorted(flags[0]) and sorted(result.unsuppressed_in) == sorted(flags[1]),
                  f"{label}: the flags J14 changes: suppressed {result.suppressed_in}, on {result.unsuppressed_in}")
        check(result.visited == ["4H", "N", "4L"], f"{label}: every other mode shown and post-checked: {result.visited}")
        say(f"        the sentence: {desk.note[0]!r}")
        update_marks(worker, desk, result, label, folder)
        raw_flag_reads(worker, desk, f"{label}, straight after", names=[m.name for m in box.mates])
        measure_modes(worker, desk, f"{label}, after", controls=True, active="2H", expected=expect)
        if drive:
            mode_drive_proof(worker, desk, f"{label}, driven in {drive}", drive)
        w8_show(worker, desk, "2H", label)
        save_assembly(worker, desk, f"{label}: 2H active again before the next edit")
        desk.plan_solidworks()

    def edit_a():
        KEY["slides"][rng]["4L"] = 66.5
        KEY["positions"]["4L"]["RangeSlv"] = ("L", 10.5)

    def edit_b():
        KEY["slides"][mod].update({"2H": 97.0, "N": 97.0})
        KEY["positions"]["4H"]["ModeSlv"] = ("4WD", 9.0)
        KEY["positions"]["4L"]["ModeSlv"] = ("4WD", 9.0)

    def edit_c():
        KEY["slides"][mod]["4H"] = 97.0
        KEY["positions"]["4H"]["ModeSlv"] = ("2WD", 0.0)
        KEY["couples"]["ModeSlv engages FrontDog"] = ("4L",)
        KEY["engaged"]["4H"] = (("RangeSlv", "InDog"),)
        KEY["rows"]["4H"] = dict(W8_REAR_FRONT["2H"])

    press("s4 RangeSlv L=+10.5", [("Gears", cell(book, "Gears", "Slides", "RangeSlv"), "H=-10, N=0, L=+10.5")], edit_a,
          [("RangeSlv", ("4L",), 0.5)], [(rng, "4L", 66.5)], drive="4L")
    press("s4 ModeSlv At 101, 4WD=+9", [("Gears", cell(book, "Gears", "At", "ModeSlv"), 101),
                                       ("Gears", cell(book, "Gears", "Slides", "ModeSlv"), "2WD=0, 4WD=+9")], edit_b,
          [("ModeSlv", ("2H", "N"), 1.0)], [(mod, "2H", 97.0), (mod, "N", 97.0)], drive="4H")
    press("s4 J14: 4H's ModeSlv 4WD -> 2WD", [("Modes", cell(book, "Modes", "ModeSlv", "4H"), "2WD")], edit_c,
          [("ModeSlv", ("4H",), -9.0)], [(mod, "4H", 97.0)], flags=([("ModeSlv engages FrontDog", "4H")], []),
          drive="4H")
    # The structural edit: a fifth mode.
    row = cell(book, "Modes", "Mode", "")[1:]
    say(f"-- s4: Excel Modes row {row}: 4X = (L, 2WD) -> structural -> Build again…")
    save_assembly(worker, desk, "s4: every Update kept before the structural edit")
    edit(desk, book, ("Modes", f"A{row}", "4X"), ("Modes", f"B{row}", "L"), ("Modes", f"C{row}", "2WD"))
    KEY["modes"] = KEY["modes"] + ("4X",)
    KEY["engaged"]["4X"] = (("RangeSlv", "LoDog"),)
    KEY["positions"]["4X"] = {"RangeSlv": ("L", 10.5), "ModeSlv": ("2WD", 0.0)}
    KEY["slides"][rng]["4X"] = 66.5
    KEY["slides"][mod]["4X"] = 97.0
    KEY["couples"]["RangeSlv engages LoDog"] = ("4L", "4X")
    KEY["rows"]["4X"] = {"Rear": 7.5, "FrontDrv": None, "Idler": None, "Front": None}
    KEY["ratios"]["4X"] = 4.0
    u = desk.update
    said = " ".join(str(x) for x in (u.structural if u is not None else ()))
    check(u is not None and u.needs_new_revision and "4X" in said, f"s4: a new mode is structural, naming 4X: {said!r}")
    f = desk.say_footer("s4, after the new mode")
    check(f.build_enabled, f"s4: Build again… offered ({f.build_label!r})")
    expect_modes_read(desk, "s4 with 4X")
    earlier, sidecars = stamps(folder), sidecar_texts(folder)

    def after_build():
        box = desk.record.gearbox
        check(box.revision == 2 and os.path.basename(box.assembly) == "TransferCase_E4_r2.SLDASM",
              f"s4: the new revision is TransferCase_E4_r2: revision {box.revision}, {os.path.basename(box.assembly)}")
        check_earlier_unchanged(folder, earlier, "s4 Build again", sidecars)
    modes_built(worker, desk, "s4 Build again", after_build=after_build)
    end_copy(worker, folder, "s4")


# -- W8 s5: the refused mate in one mode, forced (W8-PLAN §5, corrected by W8-REVIEW-TIER11 (3)) ---------------------

S5_HELD = "RangeSlv held in N"
S5_VALUE = 60.0          # mm: not N's own slide value (56); a redundant pair with equal values is unmeasured (tier 11)
S5_WATCH = {"on": False, "balloons": [], "windows": []}


def s5_doctored(plan, mode="N", value=S5_VALUE):
    """The s5 plan: the E4's GearboxPlan with a second distance mate on RangeSlv — a copy of its SLIDE ``RangeSlv along
    Rear`` at ``value`` mm, named S5_HELD — made in ``mode``'s step and on in ``mode`` only (off in every other step).
    Returns (plan, the op)."""
    slide = next(op for op in plan.assembly.ops if isinstance(op, base.Mate) and op.name == "RangeSlv along Rear")
    extra = dataclasses.replace(slide, id="inject1", value=value, name=S5_HELD)
    steps = []
    for step in plan.modes_plan.steps:
        if swbuild.on_in((mode,), step.name):
            step = dataclasses.replace(step, ops=step.ops + (extra,), on=step.on + (extra.name,))
        else:
            step = dataclasses.replace(step, off=step.off + (extra.name,))
        steps.append(step)
    modes = dataclasses.replace(plan.modes_plan, steps=tuple(steps))
    return dataclasses.replace(plan, modes_plan=modes), extra


S5_GATE = "In mode N, 'inject1' is not a gear mate, and a mode makes only couplings and sliding meshes."
S5_COUPLE = "Sun held to LoDog in N"


def s5_coupled(plan, mode="N"):
    """Part (ii)'s plan (the coordinator's ruling 3): a mode-step op the build can make, a coupling made in ``mode``'s
    step and on there alone, ``S5_COUPLE``, the Sun to LoDog 1 : 1 — a copy of 4L's ``RangeSlv engages LoDog`` with
    the Sun's handle in RangeSlv's place, listed as turning both the same way (both on Z+ along one line, so the
    gate's §9.7 rule wants it in ``same_way``). The planetary holds LoDog, on the carrier, at a quarter of the Sun's
    turn; a 1 : 1 coupling between them contradicts it, so the mode's train is over-constrained. It passes
    ``ModesPlan.check`` as it is: no patch of the app. Returns (plan, the op)."""
    handle_of = {g: h for h, g in plan.handles.items()}
    template = next(op for s in plan.modes_plan.steps for op in s.ops if op.name == "RangeSlv engages LoDog")
    extra = dataclasses.replace(template, id="inject1", name=S5_COUPLE, a=f"{handle_of['Sun']}:Gear Axis",
                                b=f"{handle_of['LoDog']}:Gear Axis")
    steps = []
    for step in plan.modes_plan.steps:
        if swbuild.on_in((mode,), step.name):
            step = dataclasses.replace(step, ops=step.ops + (extra,), on=step.on + (extra.name,))
        else:
            step = dataclasses.replace(step, off=step.off + (extra.name,))
        steps.append(step)
    modes = dataclasses.replace(plan.modes_plan, steps=tuple(steps),
                                same_way=plan.modes_plan.same_way + (extra.name,))
    return dataclasses.replace(plan, modes_plan=modes), extra


def s5_gate(worker, excel):
    """Part (i): the doctored distance mate through the app as it is -> refused at the gate, verbatim; nothing made,
    no part saved, no SolidWorks call during the build job."""
    folder, path, book, desk = write_fixture(worker, excel, "s5", spec_e4, keep="TransferCase_E4.xlsx")
    try:
        desk.say_plan(full=False)
        plan, extra = s5_doctored(desk.plan)
        say(f"        doctored: {base.describe(extra)} ({S5_HELD!r}), made in N's step, on in N, off in "
            f"{[s.name for s in plan.modes_plan.steps if extra.name in s.off]}")
        say(f"fact    s5 (i): ModesPlan.check on the doctored plan before the build: "
            f"{plan.modes_plan.check(plan.assembly)}")
        guard()
        TRACE["calls"].clear()
        TRACE.update(on=True, count=0)
        try:
            _, result = desk.build(plan)
        finally:
            TRACE["on"] = False
        said = desk.note[0] if desk.note else ""
        say(f"        the refusal verbatim: {str(desk.error)!r}")
        say(f"        the status verbatim: {said!r}")
        check(result is None and isinstance(desk.error, swbuild.BuildError) and S5_GATE in str(desk.error)
              and str(desk.error).startswith("The modes plan is not sound, so nothing is made:"),
              f"s5 (i): the build refused at the gate (swbuild._modes_gate, ModesPlan.check) with {S5_GATE!r}")
        made = sorted(n for n in os.listdir(folder) if n.upper().endswith((".SLDPRT", ".SLDASM")))
        check(not made and (desk.record is None or not desk.record.parts), f"s5 (i): nothing made, no part saved: "
              f"files {made}, record {'none' if desk.record is None else [e.path for e in desk.record.parts]}")
        check(TRACE["count"] == 0 and not TRACE["calls"], f"s5 (i): no SolidWorks call during the build job: "
              f"{TRACE['count']} calls, {TRACE['calls'][:5]}")
        say("fact    s5 (i): the step that refused: the gate, before anything is made")
    finally:
        book.close()


def section_s5(worker, excel):
    say("== s5  the refused mate in one mode, forced (W8-PLAN §5; the coordinator's ruling 3, stage 2d): (i) the plan "
        f"doctored with a second distance mate on RangeSlv ({S5_HELD!r}, {S5_VALUE:g} mm against N's 56), on in N "
        "only, through the app as it is -> refused at the gate, nothing made; (ii) the build's own handling of a mate "
        f"SolidWorks will not take in one mode: a coupling {S5_COUPLE!r} (1 : 1 against the planetary's 4 : 1) made in "
        "N's step, on in N only -> the build stops naming mode N; the parts and layout on record, no assembly file, "
        "the document left open and named; the footer never offering the same build again; closed as W5's m4 closes "
        "it. From the make to the close, an \"Over Defined\" balloon is a fact and any other window a STOP")
    s5_gate(worker, excel)
    # Part (ii). A distance op would reach the make (step 5's _mate makes any Mate), but straight after it the step
    # settles every op's turning sense as a gear mate's (_settle_sense: both handles' origins, the read, then a remake
    # with the other Flip), which a distance mate to the layout cannot go through honestly; so, as ruled, a coupling
    # the step can make, chosen so that SolidWorks cannot hold it with the planetary.
    say("-- s5 (ii): a coupling the mode step can make, refused by SolidWorks in N")
    folder, path, book, desk = write_fixture(worker, excel, "s5b", spec_e4, keep="TransferCase_E4.xlsx")
    desk.say_plan(full=False)
    plan, extra = s5_coupled(desk.plan)
    say(f"        doctored: {base.describe(extra)} ({S5_COUPLE!r}), made in N's step, on in N, off in "
        f"{[s.name for s in plan.modes_plan.steps if extra.name in s.off]}, listed in same_way")
    problems = plan.modes_plan.check(plan.assembly)
    check(not problems, f"s5 (ii): the doctored plan passes ModesPlan.check as it is (no patch of the app): {problems}")
    asm_path = os.path.join(folder, "TransferCase_E4.SLDASM")
    S5_WATCH.update(on=True, balloons=[], windows=[])
    windows = WINDOWS["count"]
    try:
        guard()
        started = time.monotonic()
        _, result = desk.build(plan)
        say(f"fact    s5 (ii): the build answered in {time.monotonic() - started:.1f} s; progress steps {desk.steps}")
        said = desk.note[0] if desk.note else ""
        say(f"        the status verbatim: {said!r}")
        if result is None:
            check(False, f"s5 (ii): the build raised instead of stopping with a result: {desk.error}")
            return
        asm = result.assembly
        problems = list(asm.mate_problems if asm else [])
        failures = list(asm.failures if asm else [])
        stopped = getattr(asm, "stopped_at", "") if asm else ""
        say(f"        mate problems {problems}; failures {failures}; stopped at {stopped!r}; left open as "
            f"{asm.document if asm else None!r}; saved {asm.saved if asm else None!r}; kind {result.kind!r}")
        statuses = run(worker, lambda s: {n: s.mate_status(n) for n in [S5_COUPLE]}) if asm and asm.document else {}
        say(f"        AddMate5 status of {S5_COUPLE}: {statuses}")
        named = [p for p in problems + [str(f[1]) for f in failures] if p.startswith("In mode N,") and S5_COUPLE in p]
        made_in_step5 = bool(stopped and "in mode N" in stopped) or any("over-defines" in p for p in named)
        say(f"fact    s5 (ii): the step that refused: "
            f"{'step 5, the make in N (or its sense read straight after)' if made_in_step5 else 'after step 5'}; the "
            f"refusal verbatim: {named}")
        check(bool(named) and made_in_step5, f"s5 (ii): the build stops at the make in step 5 naming mode N and "
              f"{S5_COUPLE}: {named or problems or failures}")
        if asm is not None and asm.document and not asm.saved:
            REFUSED.append(asm.document)
        check(asm is not None and asm.document and not asm.saved and not result.ok,
              f"s5 (ii): the assembly not saved, left open as {asm.document if asm else None!r}")
        titles = run(worker, open_titles)
        check(asm is not None and asm.document in titles, f"s5 (ii): the document is open and named: open {titles}")
        check(not os.path.exists(asm_path) and result.kind == "", f"s5 (ii): no assembly file, nothing saved in its "
              f"place: kind {result.kind!r}")
        rec = desk.record
        box = rec.gearbox if rec is not None else None
        check(rec is not None and rec.parts and box is not None and box.layout and not box.assembly
              and all(os.path.isfile(e.path) for e in rec.parts) and os.path.isfile(box.layout),
              f"s5 (ii): the parts and the layout part saved and on record, no assembly on record: parts "
              f"{[os.path.basename(e.path) for e in rec.parts] if rec else None}")
        f = desk.say_footer("s5 (ii) refused")
        check(not f.build_enabled and "Build is available again once the workbook changes" in f.text,
              "s5 (ii): the footer never offers the same build of the unchanged workbook")
        say("-- s5 (ii): the refused document closed, as W5's m4 closes it")
        left = run(worker, close_ours)
        check(not left, f"s5 (ii): closed, the refused one by its title: left {left}")
    finally:
        S5_WATCH["on"] = False
        say(f"fact    s5 (ii): from the make to the close, balloons {S5_WATCH['balloons'] or 'none'}; other windows "
            f"{S5_WATCH['windows'] or 'none'} ({WINDOWS['count'] - windows} counted)")
        book.close()


# -- W8 s7: what a configuration keeps (W8-PLAN §5, the coordinator's stage 2d) ---------------------------------------
#
# Hypothesis H (the coordinator's, from s2's two runs and tier 8's follow-up): every configuration shares a component's
# place until a put (Transform2) is made on it with a configuration showing; from then on that configuration keeps its
# own place for it and the rest go on sharing; a turn by the drive moves the shared place. Each case runs on its own
# fresh copy of s1.master; after every step every configuration is shown, rebuilt and read through fresh handles. Only
# self-consistency and the reads themselves are asserted: H broken is a result. A put SolidWorks refuses, a frame read
# None, or a window during a configuration call is a STOP.

S7 = {"cases": [], "hypotheses": {
    "shared": "shared by all: every configuration shows every turn and put",
    "per_configuration": "kept per configuration: a turn or put shows in the configuration it was made in alone",
    "H": "H: shared until a put is made on a body with a configuration showing, which from then keeps its own place "
         "for it; a turn or put made in a configuration not yet put in moves the shared place (every configuration "
         "not yet put in); one made in a configuration already put in moves that configuration alone",
    "H_private_put": "H, a put moving its own configuration alone: as H, except that a put never moves the shared place"}}
S7_ROUTE_KINDS = ("lock", "mesh", "couple", "spline")     # what the app's put route suppresses (_put_train)
S7_TOL = 1e-6


class S7Stop(Exception):
    """A STOP inside an s7 case: the case ends there, its readings kept."""


def s7_route_mates(box, mode):
    """The app's put route in ``mode``: every lock and gear mate (mesh, coupling, spline) on in ``mode``."""
    return [m.name for m in box.mates if m.kind in S7_ROUTE_KINDS and (not m.modes or any(swbuild.on_in((x,), mode)
                                                                                         for x in m.modes))]


def s7_held(box, off):
    """Each body's state during a put with ``off`` suppressed: "wholly free", or "held by" the mates left on it."""
    out = {}
    for g, _ in bodies(box):
        left = [m.name for m in box.mates if g in (m.gears or ()) and m.name not in off]
        out[g] = "wholly free" if not left else "held by " + ", ".join(left)
    return out


def s7_read_job(box):
    """Every configuration shown in mode order and rebuilt, every body found again by Name2 and its frame read; the
    configuration active before the read read first without a show (the self-consistency reading) and shown again
    last, so a read leaves the active configuration where the step left it."""
    pairs = bodies(box)

    def work(s):
        out = {"active_before": s.active_configuration(), "frames": {}, "first": {}, "rebuilt": {}}
        for i, (g, n) in enumerate(pairs):
            s.find_component(f"s7a{i}", n)
            out["first"][g] = s.component_frame(f"s7a{i}")
        for mode in box.modes:
            s.show_configuration(mode)
            out["rebuilt"][mode] = bool(s.rebuild(kind=swcom.ASSEMBLY_TRAIN))
            here = {}
            for i, (g, n) in enumerate(pairs):
                s.find_component(f"s7r{i}", n)
                here[g] = s.component_frame(f"s7r{i}")
            out["frames"][mode] = here
        s.show_configuration(out["active_before"])
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["active_after"] = s.active_configuration()
        return out
    return in_assembly(box.assembly, work)


def s7_put_job(box, mode, targets, off):
    """``mode`` shown and rebuilt; every mate in ``off`` suppressed in ``mode`` alone (marked before the call, restored
    whatever happens) and rebuilt; ``targets(before)`` (body -> frame, from the frames read just before) each put by
    ``place_component`` on a fresh handle; rebuilt; every frame read with the mates still off; the mates turned back on
    in ``mode`` (each that reads suppressed) and rebuilt; every frame read again; the mates' flags in every
    configuration."""
    pairs = bodies(box)
    name_of = dict(pairs)

    def work(s):
        out = {"errors": [], "cleanup": [], "puts": {}}
        s.show_configuration(mode)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["active"] = s.active_configuration()

        def frames(prefix):
            got = {}
            for i, (g, n) in enumerate(pairs):
                s.find_component(f"{prefix}{i}", n)
                got[g] = s.component_frame(f"{prefix}{i}")
            return got
        held = []
        try:
            for i, name in enumerate(off):
                s.find_mate(f"s7m{i}", name)
                held.append(i)
                s.set_mate_suppressed_in(f"s7m{i}", True, [mode])
            if off:
                s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["before"] = frames("s7b")
            wanted_frames = targets(out["before"])
            for i, (g, frame) in enumerate(wanted_frames.items()):
                s.find_component(f"s7p{i}", name_of[g])
                s.place_component(f"s7p{i}", frame[0], frame[1], kind=swcom.ASSEMBLY_TRAIN)
                out["puts"][g] = frame
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["mates_off"] = frames("s7o")
        except Exception as exc:  # noqa: BLE001 - said; the mates still go back on below
            out["errors"].append(f"{type(exc).__name__}: {exc}")
        finally:
            for i in held:
                try:
                    if s.mate_suppression(f"s7m{i}", [mode])[mode]:
                        s.set_mate_suppressed_in(f"s7m{i}", False, [mode])
                except Exception as exc:  # noqa: BLE001
                    out["cleanup"].append(f"{off[i]} back on: {type(exc).__name__}: {exc}")
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["mates_on"] = frames("s7n")
        out["flags"] = {off[i]: s.mate_suppression(f"s7m{i}", list(box.modes)) for i in held}
        return out
    return in_assembly(box.assembly, work)


def s7_drive_job(box, mode, degrees, plane, built_sun):
    """The drive's turn in ``mode`` (W5's angle mate, the turn repro's way): ``mode`` shown and rebuilt; the mate made
    from the input's Top plane to the layout's ``plane`` at 90° plus the input's turn from its built frame where it
    stands (so making it moves nothing, read), its value set in ``mode`` alone (``set_dimension_in``, the value
    route), rebuilt; the mate deleted and rebuilt."""
    pairs = bodies(box)
    sun = dict(pairs)[box.drag[0]]

    def work(s):
        out = {"errors": [], "cleanup": []}
        s.show_configuration(mode)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["active"] = s.active_configuration()

        def frames(prefix):
            got = {}
            for i, (g, n) in enumerate(pairs):
                s.find_component(f"{prefix}{i}", n)
                got[g] = s.component_frame(f"{prefix}{i}")
            return got
        name = ""
        try:
            out["before"] = frames("s7b")
            now = turn_degrees(built_sun[0], out["before"][box.drag[0]][0])
            if now is None:
                raise swcom.SolidWorksError(f"the input stands off its axis in {mode}, so no drive is made")
            out["input_at"] = now
            at = 90.0 + now
            s.find_component("s7sun", sun)
            s.find_component("s7lay", box.layout_component)
            name, dim = s.add_mate("s7d", "angle", "s7sun:plane2", f"s7lay:{plane}", at, "S7 drive")
            out["mate"] = (name, dim, s.mate_status(name), at)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["made"] = frames("s7m")
            s.set_dimension_in("s7d", math.radians(at + degrees) * 1000.0, [mode])
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            out["driven"] = frames("s7d")
        except Exception as exc:  # noqa: BLE001
            out["errors"].append(f"{type(exc).__name__}: {exc}")
        finally:
            if name:
                try:
                    delete_mate(s, name)
                except Exception as exc:  # noqa: BLE001
                    out["cleanup"].append(f"{name} deleted: {type(exc).__name__}: {exc}")
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        out["after"] = frames("s7f")
        out["mates"] = [m.name for m in s.mate_states()]
        return out
    return in_assembly(box.assembly, work)


def s7_run(worker, label, job):
    """A worker job of s7: a frame read None (SolidWorks' answer through a stale handle) or any other raise is a STOP
    that ends the case."""
    try:
        return run(worker, job)
    except Exception as exc:  # noqa: BLE001
        text = f"{type(exc).__name__}: {exc}"
        stop_check(False, f"{label}: the reads succeed: {text}")
        frame_none_stop([text], label)
        raise S7Stop(text) from None


def s7_express(desk, frames_by_mode):
    """Each body in each configuration as (turn about its own axis from its frame on record for that mode, degrees, or
    None off its axis; axial offset along Z from that frame, mm; radial distance of its origin from that frame's, mm)."""
    out = {}
    for mode, frames in frames_by_mode.items():
        record = mode_record_frames(desk, mode)
        here = {}
        for g, (rot, at) in frames.items():
            r_rot, r_at = record[g]
            turn = turn_degrees(r_rot, rot)
            here[g] = [None if turn is None else round(turn, 6), round(float(at[2]) - float(r_at[2]), 6),
                       round(math.hypot(float(at[0]) - float(r_at[0]), float(at[1]) - float(r_at[1])), 6)]
        out[mode] = here
    return out


def s7_table(label, expressed):
    modes = list(expressed)
    say(f"table   {label}: each body's (turn from its frame on record for the mode °, axial offset mm) "
        f"[radial offset of the origin mm where not 0]; columns {modes}")
    for g in expressed[modes[0]]:
        cells = []
        for m in modes:
            turn, axial, radial = expressed[m][g]
            t = "off-axis" if turn is None else f"{turn:+9.3f}"
            cells.append(f"{t} {axial:+7.3f}" + (f" [{radial:.3f}]" if radial > S7_TOL else ""))
        say(f"        {g:16} " + " | ".join(cells))


def s7_change(prev, now):
    """Per mode, per body, how it moved from ``prev`` to ``now`` (frames): (turn about its own axis °, or None off its
    axis; axial mm; origin moved mm), or None for a body that stands still (frame gap ≤ 1e-6)."""
    out = {}
    for mode in now:
        here = {}
        for g, frame in now[mode].items():
            if frame_gap(prev[mode][g], frame) <= S7_TOL:
                here[g] = None
                continue
            turn = turn_degrees(prev[mode][g][0], frame[0])
            here[g] = (None if turn is None else turn, float(frame[1][2]) - float(prev[mode][g][1][2]),
                       math.dist([float(v) for v in prev[mode][g][1]], [float(v) for v in frame[1]]))
        out[mode] = here
    return out


def s7_same(a, b):
    if a is None or b is None:
        return a is None and b is None
    if (a[0] is None) != (b[0] is None):
        return False
    return (a[0] is None or abs(a[0] - b[0]) <= 1e-5) and abs(a[1] - b[1]) <= 1e-5 and abs(a[2] - b[2]) <= 1e-5


def s7_judge(box, label, step, kind, made_in, prev, now, forked):
    """Which hypothesis the step's reading fits, per body that moved where the step was made: each other configuration
    "moved" (the same change as ``made_in``), "still", or "other"; each hypothesis's predicted set of configurations
    that move; fits where they agree for every such body. ``forked``: body -> configurations put in BEFORE this step
    (updated here for a put). Returns the judgement for the JSON."""
    change = s7_change(prev, now)
    moved_bodies = [g for g, c in change[made_in].items() if c is not None]
    seen, fits = {}, {h: True for h in S7["hypotheses"]}
    modes = list(box.modes)
    for g in moved_bodies:
        state = {m: ("moved" if s7_same(change[m][g], change[made_in][g]) else
                     "still" if change[m][g] is None else "other") for m in modes}
        observed = {m for m, v in state.items() if v == "moved"}
        before = forked.get(g, set())
        unforked = {m for m in modes if m not in before}
        predicted = {"shared": set(modes), "per_configuration": {made_in}}
        if made_in in before:
            predicted["H"] = predicted["H_private_put"] = {made_in}
        else:
            predicted["H"] = unforked | {made_in}
            predicted["H_private_put"] = {made_in} if kind == "put" else unforked | {made_in}
        seen[g] = {"change_where_made": change[made_in][g], "state": state, "forked_before": sorted(before),
                   "predicted": {h: sorted(p) for h, p in predicted.items()}}
        for h, p in predicted.items():
            if observed != p or any(v == "other" for v in state.values()):
                fits[h] = False
    fit = [h for h, ok in fits.items() if ok] if moved_bodies else []
    out = [h for h, ok in fits.items() if not ok] if moved_bodies else []
    say(f"judge   {label}, {step}: bodies moved in {made_in}: {moved_bodies or 'none (nothing to judge)'}")
    for g, v in seen.items():
        say(f"        {g:16} {v['state']} (put in before: {v['forked_before'] or 'none'})")
    say(f"        fits {(fit or 'none') if moved_bodies else 'nothing to judge'}; rules out {out or '-'}")
    return {"step": step, "kind": kind, "made_in": made_in, "moved_bodies": moved_bodies, "bodies": seen,
            "fits": fit, "rules_out": out}


def s7_note_put(forked, mode, bodies_put):
    for g in bodies_put:
        forked.setdefault(g, set()).add(mode)


class S7Case:
    """One s7 case on its own copy: the readings, tables and judgements kept for the JSON."""

    def __init__(self, worker, excel, key, title):
        self.worker, self.key, self.title = worker, key, title
        say(f"-- s7 case {key}: {title}")
        self.folder, self.path, self.book, self.desk, self.built = start_w8_copy(worker, excel, f"s7-{key}")
        self.box = self.desk.record.gearbox
        self.forked = {}
        self.reads = []
        self.judged = []
        self.last = None
        self.json = {"case": key, "title": title, "copy": os.path.basename(self.folder), "steps": []}
        S7["cases"].append(self.json)

    def read(self, step):
        label = f"s7 {self.key} {step}"
        out = s7_run(self.worker, label, s7_read_job(self.box))
        active = out["active_before"]
        gap, at = frames_gap(out["first"], out["frames"][next(m for m in self.box.modes if swbuild.on_in((m,), active))])
        check(gap <= S7_TOL and all(out["rebuilt"].values()) and swbuild.on_in((active,), out["active_after"]),
              f"{label}: every configuration shown and rebuilt; {active}, active, read the same before any show and "
              f"after its own (largest {gap:.1e} at {at or '-'}); left active again ({out['active_after']})")
        expressed = s7_express(self.desk, out["frames"])
        s7_table(f"{label} (active {active})", expressed)
        self.json["steps"].append({"step": step, "active": active, "expressed": expressed,
                                   "frames": {m: {g: [list(f[0]), list(f[1])] for g, f in fr.items()}
                                              for m, fr in out["frames"].items()}})
        return out["frames"]

    def judge(self, step, kind, made_in, now, bodies_put=()):
        if self.last is not None:
            j = s7_judge(self.box, f"s7 {self.key}", step, kind, made_in, self.last, now, self.forked)
            self.json["steps"][-1]["judgement"] = j
            self.judged.append(j)
        if kind == "put":
            s7_note_put(self.forked, made_in, bodies_put)
        self.last = now

    def put(self, step, mode, targets, route=True):
        """A put in ``mode`` (the app's route when ``route``), then every configuration read and judged."""
        off = s7_route_mates(self.box, mode) if route else []
        held = s7_held(self.box, off)
        label = f"s7 {self.key} {step}"
        out = s7_run(self.worker, label, s7_put_job(self.box, mode, targets, off))
        if out["errors"] or out["cleanup"]:
            stop_check(False, f"{label}: SolidWorks took the put and the mates went back on: {out['errors']} "
                              f"{out['cleanup']}")
            frame_none_stop(out["errors"] + out["cleanup"], label)
            raise S7Stop(f"{label}: {out['errors']} {out['cleanup']}")
        wrong = {n: f for n, f in out["flags"].items() if any(bool(v) != key_suppressed(n, c) for c, v in f.items())}
        check(swbuild.on_in((mode,), out["active"]) and not wrong, f"{label}: put in {out['active']}; every mate "
              f"suppressed for the put back as §2.3 has it in every configuration: wrong {wrong}")
        put_bodies = list(out["puts"])
        moved = {g: frame_gap(out["before"][g], f) for g, f in out["puts"].items()}
        say(f"step    {label}: put in {mode} by {'the app' if route else 'a plain Transform2'}'s route, mates off "
            f"there {off or 'none'}; each body put and how far from where it stood {({g: round(v, 6) for g, v in moved.items()})}")
        say(f"        during the put: {({g: held[g] for g in put_bodies})}")
        for when in ("mates_off", "mates_on"):
            gap, at = frames_gap(out[when], {g: out["puts"][g] for g in put_bodies})
            say(f"        in {mode}, {when.replace('_', ' ')}: every body put stands where it was put, largest "
                f"{gap:.1e} at {at or '-'}; others moved {[g for g in out[when] if g not in out['puts'] and frame_gap(out['before'][g], out[when][g]) > S7_TOL]}")
        frames = self.read(step)
        self.json["steps"][-1].update(put={"mode": mode, "route": "app" if route else "plain", "mates_off": off,
                                           "bodies": put_bodies, "held": {g: held[g] for g in put_bodies},
                                           "moved_mm_or_rad": moved,
                                           "in_mode_mates_off": s7_express(self.desk, {mode: out["mates_off"]})[mode],
                                           "in_mode_mates_on": s7_express(self.desk, {mode: out["mates_on"]})[mode]})
        self.judge(step, "put", mode, frames, put_bodies)
        return frames

    def drive(self, step, mode, degrees):
        label = f"s7 {self.key} {step}"
        plane, _ = drive_assumptions(self.desk, box_drag(self.box), label)
        built_sun = wanted(self.desk)[box_drag(self.box)]
        out = s7_run(self.worker, label, s7_drive_job(self.box, mode, degrees, plane, built_sun))
        if out["errors"] or out["cleanup"] or "driven" not in out:
            stop_check(False, f"{label}: the drive turned and was deleted: {out['errors']} {out['cleanup']}")
            raise S7Stop(f"{label}: {out['errors']} {out['cleanup']}")
        sun = box_drag(self.box)
        gap = max(frame_gap(out["before"][g], out["made"][g]) for g in out["before"])
        turned = turn_degrees(out["before"][sun][0], out["after"][sun][0])
        check(gap <= S7_TOL and turned is not None and abs(turned - degrees) <= DRIVE_TOLERANCE * abs(degrees)
              and "S7 drive" not in out["mates"] and swbuild.on_in((mode,), out["active"]),
              f"{label}: in {out['active']} the drive made at {out['mate'][3]:.6f}° (the input at "
              f"{out['input_at']:+.6f}°) moved nothing ({gap:.1e}), turned {sun} {turned}° for {degrees:+g}°, and was "
              f"deleted")
        say(f"step    {label}: the drive's {degrees:+g}° in {mode}")
        frames = self.read(step)
        self.json["steps"][-1].update(drive={"mode": mode, "degrees": degrees, "input_at": out["input_at"]})
        self.judge(step, "turn", mode, frames)
        return frames

    def reopen(self, step):
        """Saved (this run's modified documents, as a person would), closed, reopened, every configuration read."""
        active = run(self.worker, in_assembly(self.box.assembly, lambda s: s.active_configuration()))
        left = run(self.worker, close_ours)
        check(not left, f"s7 {self.key} {step}: saved with {active} active and closed: left {left}")
        run(self.worker, lambda s: live_open(s, self.box.assembly))
        again = run(self.worker, in_assembly(self.box.assembly, lambda s: s.active_configuration()))
        say(f"step    s7 {self.key} {step}: reopened in {again} (saved with {active} active)")
        prev = self.last
        frames = self.read(step)
        if prev is not None:
            gaps = {m: frames_gap(frames[m], prev[m]) for m in frames}
            same = all(g <= S7_TOL for g, _ in gaps.values())
            check(same, f"s7 {self.key} {step}: every configuration reads after the reopen as before the save "
                        f"(largest per mode {({m: f'{g:.1e} at {a or chr(45)}' for m, (g, a) in gaps.items()})})")
            self.json["steps"][-1]["same_as_before_save"] = same
        self.json["steps"][-1]["reopened_in"] = again
        self.last = frames
        return frames

    def end(self):
        end_copy(self.worker, self.folder, f"s7-{self.key}")       # closes the copy's documents and Excel's workbook


def box_drag(box):
    return box.drag[0]


def s7_noop(desk, only=None):
    """A put's targets: every mated body (or ``only``) put where it stands."""
    box = desk.record.gearbox
    names = [g for g, _ in bodies(box) if g not in box.fixed and (only is None or g in only)]
    return lambda before: {g: before[g] for g in names}


def s7_axial(body, dz):
    return lambda before: {body: (before[body][0], (before[body][1][0], before[body][1][1], before[body][1][2] + dz))}


def s7_spin(body, degrees):
    return lambda before: {body: (turn_about_z(before[body][0], degrees), before[body][1])}


def s7_built_check(case, frames):
    """Case 1's first read: does the copy as built differ between configurations, and from the frames on record?"""
    box = case.box
    off = {m: frames_gap(frames[m], mode_record_frames(case.desk, m)) for m in box.modes}
    first = box.modes[0]
    differ = {}
    for m in box.modes[1:]:
        differ[m] = [g for g in frames[m] if frame_gap(frames[m][g], frames[first][g]) > S7_TOL]
    say(f"fact    s7 {case.key}: as copied, each configuration against its frames on record: "
        f"{({m: f'{g:.1e} at {a or chr(45)}' for m, (g, a) in off.items()})}; bodies standing differently from "
        f"{first}: {differ} (the sliders' slide values differ by design)")
    case.json["as_built"] = {"against_record": {m: g for m, (g, _) in off.items()}, "differ_from_first": differ}


def s7_case_1(worker, excel):
    c = S7Case(worker, excel, "1", "virgin: straight from the copy, read; the drive's +37° in 2H; read; reopen")
    try:
        frames = c.read("as copied")
        s7_built_check(c, frames)
        c.last = frames
        c.drive("drive +37 in 2H", "2H", 37.0)
        c.reopen("saved and reopened")
    finally:
        c.end()


def s7_case_2(worker, excel):
    c = S7Case(worker, excel, "2", "a no-op put forks? 4L (not the configuration the copy opens in): the app's put "
                                   "route to the same frames; then the drive's +37° in 2H")
    try:
        c.last = c.read("as copied")
        c.put("no-op put in 4L", "4L", s7_noop(c.desk))
        c.drive("drive +37 in 2H", "2H", 37.0)
        c.reopen("saved and reopened")
    finally:
        c.end()


def s7_case_3(worker, excel):
    c = S7Case(worker, excel, "3", "every configuration put in: the no-op put in 2H, 4H, N and 4L in turn; the drive's "
                                   "+37° in 2H; +20° in 4L; save and reopen; +11° in N")
    try:
        c.last = c.read("as copied")
        for mode in c.box.modes:
            c.put(f"no-op put in {mode}", mode, s7_noop(c.desk))
        c.drive("drive +37 in 2H", "2H", 37.0)
        c.drive("drive +20 in 4L", "4L", 20.0)
        c.reopen("saved and reopened")
        c.drive("drive +11 in N after the reopen", "N", 11.0)
        c.reopen("saved and reopened again")
    finally:
        c.end()


def s7_case_4(worker, excel):
    c = S7Case(worker, excel, "4", "after the app's own Update: At 130 -> 132 (every mode put); the drive's +37° in 2H")
    try:
        c.last = c.read("as copied")
        say("-- s7 4: Excel FDrive, FIdler and FOut At 130 -> 132 -> Update (through the app)")
        edit(c.desk, c.book, *[("Gears", cell(c.book, "Gears", "At", g), 132) for g in ("FDrive", "FIdler", "FOut")])
        result, calls, seconds = w8_update(worker, c.desk, "s7 4 changed Update")
        check(result is not None and result.ok, f"s7 4: the changed Update went through: "
              f"{result and result.failures} {desk_note(c.desk)!r}")
        put_in = list(result.put_in) if result is not None else []
        c.json["update"] = {"put_in": put_in, "visited": list(result.visited) if result else [], "seconds": seconds,
                            "status": desk_note(c.desk)}
        moved = {}
        for mode, names in puts_by_mode(calls, "2H"):
            moved.setdefault(mode, []).extend(names)
        gear_of = {n: g for g, n in bodies(c.box)}
        frames = c.read("after the changed Update")
        # The Update moved the workbook's gears: the frames on record are the new ones now (the record was rewritten),
        # so nothing is judged across it; it forks every configuration it put in, for every body it put there.
        for mode, names in moved.items():
            s7_note_put(c.forked, mode, [gear_of.get(n, n) for n in names])
        say(f"fact    s7 4: the Update put in {put_in}; bodies put by configuration {moved}")
        c.last = frames
        c.drive("drive +37 in 2H", "2H", 37.0)
        c.reopen("saved and reopened")
    finally:
        c.end()


def desk_note(desk):
    return desk.note[0] if desk.note else ""


def s7_case_5(worker, excel):
    c = S7Case(worker, excel, "5", "a free component (the plan's case): FIdler +20° in N by a plain Transform2, its "
                                   "mates on; +10° in 4H; FDrive +2 mm along its axis by the app's route in 2H")
    try:
        c.last = c.read("as copied")
        c.put("FIdler +20 in N, plain", "N", s7_spin("FIdler", 20.0), route=False)
        c.put("FIdler +10 in 4H, plain", "4H", s7_spin("FIdler", 10.0), route=False)
        c.put("FDrive +2 mm in 2H, the app's route", "2H", s7_axial("FDrive", 2.0))
        c.reopen("saved and reopened")
    finally:
        c.end()


def s7_case_7(worker, excel):
    c = S7Case(worker, excel, "7", "the plan's other readings: RangeSlv along Rear's 4L value set with 2H active; a "
                                   "handle held across a show; the layout's IsFixed through fresh handles in each "
                                   "configuration")
    box = c.box
    sun = dict(bodies(box))[box_drag(box)]

    def work(s):
        out = {}
        s.show_configuration("2H")
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        s.find_mate("s7v", "RangeSlv along Rear")
        out["values_before"] = s.dimension_values("s7v", list(box.modes))
        target = out["values_before"]["4L"] + 3.0
        s.set_dimension_in("s7v", target, ["4L"])
        out["values_set"] = s.dimension_values("s7v", list(box.modes))
        out["active_after_set"] = s.active_configuration()
        s.set_dimension_in("s7v", out["values_before"]["4L"], ["4L"])
        out["values_restored"] = s.dimension_values("s7v", list(box.modes))
        out["target"] = target
        s.find_component("s7h", sun)
        s.find_component("s7l", box.layout_component)
        # Fetched now (Session.raw_component) and held across the show on purpose: the plan's reading of what a
        # handle kept over a configuration change answers. Nothing after it uses them.
        comp = s.raw_component("s7h")
        lay = s.raw_component("s7l")
        out["held_before"] = (s.component_frame("s7h"), s.is_fixed("s7l"))
        s.show_configuration("4H")
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        try:
            t = call(comp, "Transform2")
            out["held_transform"] = None if t is None else [float(v) for v in call(t, "ArrayData")][:12]
        except Exception as exc:  # noqa: BLE001
            out["held_transform"] = f"{type(exc).__name__}: {exc}"
        try:
            out["held_is_fixed"] = bool(call(lay, "IsFixed"))
        except Exception as exc:  # noqa: BLE001
            out["held_is_fixed"] = f"{type(exc).__name__}: {exc}"
        out["fresh_is_fixed"] = {}
        for mode in box.modes:
            s.show_configuration(mode)
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            s.find_component(f"s7f{mode}", box.layout_component)
            s.find_component(f"s7r{mode}", dict(bodies(box))[box.fixed[0]])
            out["fresh_is_fixed"][mode] = (s.is_fixed(f"s7f{mode}"), s.is_fixed(f"s7r{mode}"))
        s.show_configuration("2H")
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        return out
    try:
        out = s7_run(worker, "s7 7", in_assembly(box.assembly, work))
        say(f"fact    s7 7: RangeSlv along Rear before {out['values_before']}; 4L set to {out['target']:g} with "
            f"{out['active_after_set']} active -> {out['values_set']}; set back -> {out['values_restored']}")
        others = all(abs(out["values_set"][m] - out["values_before"][m]) <= 1e-6 for m in box.modes if m != "4L")
        check(abs(out["values_set"]["4L"] - out["target"]) <= 1e-6 and others
              and swbuild.on_in(("2H",), out["active_after_set"])
              and all(abs(out["values_restored"][m] - out["values_before"][m]) <= 1e-6 for m in box.modes),
              "s7 7: 4L's value set and read back without activating 4L, the others unchanged, set back")
        say(f"fact    s7 7: a handle held across a show of 4H (fetched in 2H): Transform2 {out['held_transform']!r}; the "
            f"layout's IsFixed {out['held_is_fixed']!r} (fresh in 2H before the show: frame read, IsFixed "
            f"{out['held_before'][1]})")
        say(f"fact    s7 7: IsFixed through handles fetched after each show, (layout, {box.fixed[0]}): "
            f"{out['fresh_is_fixed']}")
        check(all(a is True and b is True for a, b in out["fresh_is_fixed"].values()),
              "s7 7: the layout and the fixed ring read IsFixed True through fresh handles in every configuration")
        c.json["readings"] = {k: v for k, v in out.items() if k != "held_before"}
    finally:
        c.end()


def s7_per_body():
    """Case 6 (the review's (c)): for every put of cases 2-5, each body put, whether it was held by its axis mates or
    wholly free during the put, and how the configurations other than the put's read after it."""
    rows = []
    for case in S7["cases"]:
        for step in case["steps"]:
            put, j = step.get("put"), step.get("judgement")
            if not put or not j:
                continue
            for g in put["bodies"]:
                state = j["bodies"].get(g, {}).get("state")
                rows.append({"case": case["case"], "step": step["step"], "body": g, "during": put["held"][g],
                             "configurations": state or "did not move where it was put"})
    say("table   s7 6: each body put, held or wholly free during the put, and how each configuration read after it")
    for r in rows:
        say(f"        {r['case']} {r['step']}: {r['body']:16} {r['during'][:60]:60} {r['configurations']}")
    S7["per_body"] = rows


def section_s7(worker, excel):
    say("== s7  what a configuration keeps (W8-PLAN §5, the coordinator's stage 2d): each case on its own copy of "
        "s1.master; after every step every configuration shown, rebuilt and read through fresh handles; saved, "
        "reopened, read again; each reading judged against \"shared by all\", \"kept per configuration\" and H")
    started = time.strftime("%Y%m%d-%H%M%S")
    S7.update(revision=list(TAG["revision"]), snapshot=snapshot().strip(' ()').replace('snapshot: ', ''), finding_turn=swcom.positions_per_configuration(
        TAG["revision"]), cases=[])
    path = os.path.join(os.path.dirname(os.path.abspath(LOG_PATH)), f"w8-s7-{started}.json")
    try:
        for case in (s7_case_1, s7_case_2, s7_case_3, s7_case_4, s7_case_5, s7_case_7):
            guard()
            try:
                case(worker, excel)
            except S7Stop as exc:
                say(f"        s7: the case stopped at a STOP ({exc}); the next case goes on")
        s7_per_body()
    finally:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(S7, handle, indent=1, default=str)
        say(f"result  s7's readings written to {path}")


SECTIONS = {"m1": section_m1, "m2": section_m2, "m3": section_m3, "m4": section_m4, "m5": section_m5, "m6": section_m6,
            "m7": section_m7, "m8": section_m8, "rs1": section_rs1, "rs2": section_rs2, "rs3": section_rs3,
            "a": section_a, "a2": section_a2, "a3": section_a3, "b": section_b, "c": section_c,
            "r1": section_r1, "r2": section_r2, "r3": section_r3, "r4": section_r4, "r5": section_r5,
            "r6": section_r6, "r7": section_r7, "r8": section_r8,
            "p1": section_p1, "p2": section_p2, "p3": section_p3, "p4": section_p4, "p5": section_p5,
            "p6": section_p6, "p7": section_p7,
            "s0": section_s0, "s1": section_s1, "s2": section_s2, "s3": section_s3, "s4": section_s4,
            "s5": section_s5, "s7": section_s7}


def connect_pid():
    found = [c for c in swcom.find_candidates() if c.pid == PID]
    if not found:
        raise swcom.NotRunning(f"No SolidWorks session with PID {PID} is reachable.")
    return swcom.Session(found[0].app, found[0].revision, found[0].pid)


def snapshot():
    """What the snapshot beside ``src`` was taken from (its SNAPSHOT_COMMIT file, written when it was archived)."""
    path = os.path.join(os.path.dirname(os.path.abspath(SRC)), "SNAPSHOT_COMMIT")
    try:
        with open(path, encoding="utf-8") as handle:
            return f" (snapshot: {handle.read().strip()})"
    except OSError:
        return ""


def give_back_r1():
    """At the very end, once nothing copies from them any more: r1.master and p1.master renamed back to r1 and p1, so
    the person's steps open them where their records and the assemblies' references point."""
    for section, person, assembly in (("r1", PERSON_W6, "Bevel_Reducer.SLDASM"),
                                      ("p1", PERSON_W7, "Planetary_4to1.SLDASM")):
        master = os.path.join(OUT, section + MASTER_SUFFIX)
        target = os.path.join(OUT, section)
        if not os.path.isdir(master):
            continue
        if os.path.exists(target):
            say(f"{section:<7} {target} exists; {section}.master left as it is")
            continue
        try:
            os.rename(master, target)
        except OSError as exc:
            say(f"{section:<7} {section}.master could not be renamed back to {section}: {exc}")
            continue
        person[:] = [os.path.join(target, assembly)]
        say(f"{section:<7} {section}.master renamed back to {section} for the person's step: {target}")


def person_step():
    """W5-PLAN §4.4: the step only a person can do, with the assembly to open."""
    where = next((p for what, p in PERSON if what == "a2"), "") or next((p for _, p in PERSON), "")
    say("person  W5-PLAN §4.4, the step only a person can do (for 2026, then 2024):")
    say(f"person  In SolidWorks, open {where or 'the Reducer_12to1.SLDASM a section built (a2 or m4)'}. Click gear "
        "G1 — the small gear on S1, at the origin — and drag it round its axis by about a quarter turn. Watch G4, the "
        "large gear on S3: it turns the same way as G1, much more slowly — a quarter turn of G1 turns G4 about 7.5°. "
        "G2 and G3, on S2, turn together the other way. No gear should leave its axis, slide along it, or pass "
        "through another. Then, in the Workbook window, press Update SolidWorks with nothing changed: the footer "
        "should say the gears stand where they were turned. Tell us what you saw, on each version.")
    if PERSON_W6:
        say("person  W6-PLAN §6.1, the step only a person can do (for 2026, then 2024):")
        say(f"person  In {os.path.dirname(PERSON_W6[0])}, open Bevel_Reducer.xlsx in the Workbook window and "
            f"{os.path.basename(PERSON_W6[0])} in SolidWorks. Drag G1 — the small bevel gear on the "
            "horizontal shaft S1 — round its axis by about a quarter turn. G2, the large bevel gear on the upright "
            "shaft, turns half as far, and G3 under it with it; G4, the large spur gear on S3, turns a sixth as far as "
            "G1 and the other way round from G2. Nothing leaves its axis or passes through another gear. Then press "
            "Update SolidWorks with nothing changed: the footer says the gears stand where they were turned.")
    if PERSON_W7:
        say("person  W7-PLAN §6, the step only a person can do (for 2026, then 2024):")
        say(f"person  In {os.path.dirname(PERSON_W7[0])}, open Planetary_4to1.xlsx in the Workbook window and "
            f"{os.path.basename(PERSON_W7[0])} in SolidWorks. Drag Sun round its axis by about a quarter turn, and "
            "watch the three planets: they roll round inside the ring the same way as Sun, about a quarter as fast, "
            "each spinning the other way on its own axis; the ring does not move. Then press Update SolidWorks with "
            "nothing changed: the footer should say the gears stand where they were turned.")


def main():
    os.makedirs(OUT, exist_ok=True)
    say(f"run     {time.strftime('%Y-%m-%d %H:%M:%S')}; app {WRITTEN_BY} from {SRC}{snapshot()}; sections {ONLY}")
    unknown = [n for n in ONLY if n not in SECTIONS]
    if unknown:
        say(f"STOP    no such section {unknown}; there are {list(SECTIONS)}")
        return 2
    worker = swcom.Worker(connect_pid)
    CURRENT["worker"] = worker
    label, pid, revision = run(worker, lambda s: (s.label, s.pid, s.revision), 120)
    TAG["major"] = revision[0]
    TAG["version"] = ".".join(str(v) for v in revision)
    TAG["revision"] = tuple(revision)
    say(f"attach  {label}, PID {pid}; {memory()}")
    if pid != PID:
        say(f"STOP    attached to PID {pid}, not {PID}")
        worker.shutdown()
        return 2
    before = run(worker, open_titles, 120)
    say(f"open    before: {before}")
    say(f"findings LAYOUT_PLUS_FLIP {findings.LAYOUT_PLUS_FLIP}, LAYOUT_NEGATED_LINK {findings.LAYOUT_NEGATED_LINK!r}, "
        f"LAYOUT_AXIS_Z_SIGN {findings.LAYOUT_AXIS_Z_SIGN}, REPLACE_FIXED_ROUTE {findings.REPLACE_FIXED_ROUTE!r}")
    say(f"findings W5: GEAR_MATE_RATIO_ROUTE {findings.GEAR_MATE_RATIO_ROUTE!r}, MATED_ASSEMBLY_REBUILD_ROUTE "
        f"{findings.MATED_ASSEMBLY_REBUILD_ROUTE!r}, MATED_BUILD_REBUILD_ROUTE {findings.MATED_BUILD_REBUILD_ROUTE!r}, "
        f"GEAR_MATE_FLIP {findings.GEAR_MATE_FLIP}, DEMONSTRATION_DRIVE_SENSE {findings.DEMONSTRATION_DRIVE_SENSE}, "
        f"MESH_PHASE_ROUTE {findings.MESH_PHASE_ROUTE!r}, LOCK_RETAKES_AN_OFFSET {findings.LOCK_RETAKES_AN_OFFSET}; "
        f"P0c {p0c_findings()}; AXIAL_RESTORES {AXIAL_RESTORES}; m4 offset {M4_OFFSET:g} mm")
    say(f"findings W6: TURNED_GEAR_MATE_SENSE_READ_BACK "
        f"{getattr(findings, 'TURNED_GEAR_MATE_SENSE_READ_BACK', None)!r}, TURNED_GEAR_MATE_SENSE_ANGLES "
        f"{getattr(findings, 'TURNED_GEAR_MATE_SENSE_ANGLES', None)}, TURNED_GEAR_MATE_SENSE_ANGLES_SKEW "
        f"{getattr(findings, 'TURNED_GEAR_MATE_SENSE_ANGLES_SKEW', None)}, GEAR_MATE_SENSE_READ_BACK "
        f"{getattr(findings, 'GEAR_MATE_SENSE_READ_BACK', None)!r}, LAYOUT_PLUS_FLIP {findings.LAYOUT_PLUS_FLIP}, "
        f"REF_PLANE_UNFLIPPED_IS_PLUS_Z {getattr(findings, 'REF_PLANE_UNFLIPPED_IS_PLUS_Z', None)}, AXIAL_MATE_ROUTE "
        f"{getattr(findings, 'AXIAL_MATE_ROUTE', None)!r}")
    say(f"findings W8: CONFIGURATION_SHOW_RAISES_DIALOG {getattr(findings, 'CONFIGURATION_SHOW_RAISES_DIALOG', None)}, "
        f"HANDLES_STALE_AFTER_CONFIGURATION_CHANGE {getattr(findings, 'HANDLES_STALE_AFTER_CONFIGURATION_CHANGE', None)}, "
        f"SLIDE_VALUE_ROUTE {getattr(findings, 'SLIDE_VALUE_ROUTE', None)!r}, TURN_PER_CONFIGURATION_ON_2026 "
        f"{getattr(findings, 'TURN_PER_CONFIGURATION_ON_2026', None)}, _ON_2024 "
        f"{getattr(findings, 'TURN_PER_CONFIGURATION_ON_2024', None)} (the app's finding), "
        f"POSITIONS_PER_CONFIGURATION_ON_2026 {getattr(findings, 'POSITIONS_PER_CONFIGURATION_ON_2026', None)}, _ON_2024 "
        f"{getattr(findings, 'POSITIONS_PER_CONFIGURATION_ON_2024', None)} (the put fact, read by nothing), "
        f"SUPPRESSED_GEAR_MATE_SENSE_READ "
        f"{getattr(findings, 'SUPPRESSED_GEAR_MATE_SENSE_READ', None)!r}, COLLINEAR_GEAR_MATE_SENSE_READ_BACK "
        f"{getattr(findings, 'COLLINEAR_GEAR_MATE_SENSE_READ_BACK', None)}; "
        f"swcom.positions_per_configuration(revision) here {swcom.positions_per_configuration(TAG['revision'])}")
    watch = DialogWatch()
    watch.start()
    excel = xlhelp.Excel(visible=True)
    say(f"excel   started our own Excel, PID {excel.pid}, {excel.version}")
    try:
        for name in ONLY:
            if TAG["major"] == 32 and free_gb() < 3.0:
                say(f"SKIP    section {name}: {memory()}, under the 3 GB a 2024 section starts with")
                continue
            started = time.monotonic()
            halted = False
            try:
                SECTIONS[name](worker, excel)
            except Stopped as exc:
                check(False, f"section {name} stopped: {exc}")
                halted = True
            except Halt as exc:
                check(False, f"section {name} HALTED, the run stops here (W5-PLAN §4.2): {exc}")
                halted = True
            except Exception as exc:  # noqa: BLE001 - logged, and the documents still closed below
                check(False, f"section {name} raised {type(exc).__name__}: {exc}")
                frame_none_stop([str(exc)], f"section {name}")
                for line in traceback.format_exc().splitlines():
                    say("        " + line)
            finally:
                books = close_books()
                if books:
                    say(f"excel   section {name} left {books} open in Excel: closed without saving")
                left = run(worker, close_ours, 600)
                say(f"close   section {name}: left of ours {left}; {time.monotonic() - started:.0f} s; {memory()}")
            if halted:
                break
    finally:
        try:
            excel.quit()
            say("excel   quit our own Excel")
        except Exception as exc:  # noqa: BLE001
            say(f"excel   quit trouble: {exc}")
        left = run(worker, close_ours, 600)
        after = run(worker, open_titles, 120)
        say(f"close   left of ours {left}; stray {[t for t in after if t not in before]}; "
            f"lost {[t for t in before if t not in after]}; {memory()}")
        watch.stop.set()
        say(f"dialogs progress boxes seen {PROGRESS}; other dialogs are logged above as DIALOG")
        worker.shutdown()
    give_back_r1()
    for line in NOTES:
        say(f"noted   {line}")
    for line in STOPS:
        say(f"stop    W8-PLAN §0.5: {line}")
    person_step()
    say(f"done    {len(FAILS)} failed: {FAILS}; {len(NOTES)} noted for a ruling")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    code = 1
    try:
        code = main()
    finally:
        with open(LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(LOG) + "\n")
    raise SystemExit(code)
