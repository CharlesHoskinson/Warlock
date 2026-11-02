# Haskell process custody

Status: the standalone package passed a fresh offline strict build and its focused internal and public test suites under protected CPU QA with an owned child cgroup. See `qualification.json` for exact evidence and limits. This package contains the reviewed selected-descriptor process core, checked absolute-deadline handoff and internal scoped stop request, with an opaque caller facade. These focused tests do not transfer the historical 66-control result or establish namespace, native GUI or original-scenario acceptance. `HANDOFF.md` preserves the author’s pre-execution proposal.

## Tutorial

A caller may create one `Owner`, construct an absolute `AdmissionDeadline`, and use `runTool` for the exact supported pinned tools. Inspect `status` after each operation. `Quarantined` is retained custody, not successful cleanup; keep the owner alive and hand it to the trusted supervisor. Do not drop a quarantined owner or assume a close proves process retirement.

## How-to for root

Review the exact files and original qualification, then use the protected launcher and commands in HANDOFF. The fixture executable is built from this package; pass its actual `cabal list-bin` result to the internal test and record its resulting hash. Root must provide external bounded child containment for any test failure. Do not substitute system paths or a previously qualified fixture hash.

## Reference

The public module exports abstract `Owner`, `HeldExecutable`, `TransferTicket`, `SelectedSpawn`, `Session`, and `AdmissionDeadline`. `runTool` accepts only its existing fixed tools and verified hashes; selected use needs an already issued lease and ticket. Neither raw FD, issuer, fixture hook, owner mutations nor transfer owner tokens are exposed. `deadlineAfter` constructs the existing single absolute admission budget; cleanup may exceed it to retain custody.

## Explanation

The current canonical validated issuer lives in `warlock-held-document-proposal` (`Warlock.Platform.Executable`); this package's Lease module reexports that same opaque type. The public `Warlock.Capture.Process.Bootstrap` facade uses the existing selected-process/session/ticket operations and exposes no raw-FD issuer or transfer capability. The separate [runtime](../runtime/README.md) joins selected-session authentication and endpoint ownership through public package boundaries. A potentially alive quarantined child still needs a persistent supervisor; this component alone is not one. Original scenario, native and release claims remain open.

The internal diagnostic observation keeps complete bounded stdout/stderr when an operation exits unsuccessfully. The operation remains `Unsuccessful`; timeout, overflow and incomplete captures do not claim complete diagnostics. It uses the existing readers and deadline. Focused package controls cover failure bytes, legacy verdicts, success, overflow, timeout and isolation between invocations.

The internal selected descriptor route uses child-only POSIX spawn file actions, leaving parent descriptor flags unchanged. It installs the ordered borrowed descriptors at 3..N+2, closes unrelated child descriptors, creates a process group and retains pending PID, pipe and native-storage custody in the same Owner. It reuses the bounded readers, deadline, scoped observation and sole-reaper lifecycle. The package pins the reviewed process 1.6.19.0 API.

The current route accepts up to 256 selected descriptors and no selected stdin/ticket combination. Its twelve focused controls include deliberately inheritable ambient file and socket sentinels, failed exit output, deadline refusal and retained post-publication quarantine. Prepublication quarantine retains custody; it is not a general recovery mechanism. The upper-bound test passes 256 live descriptors aliasing one file, verifies every child mapping and checks unchanged parent flags. This supports the descriptor count; it does not qualify a whole GUI manifest. No native window behavior follows from these tests.

The trusted internal bootstrap can import/export the exact absolute monotonic deadline. Import refuses malformed or expired values and values more than 30 seconds ahead; it preserves the supplied deadline without renewal. The selected-FD `Until` entry uses that same deadline. Its tool hash read precedes core admission, so this is not a separate deadline guarantee for prehashing.

The internal `selectedHeldNoInput` uses an already issued opaque executable lease and an explicit environment. It closes child stdin rather than promising EOF or `/dev/null`; the qualified resolver fixture checks that the caller's stdin object is not inherited. It does not expose a new public issuer.

The internal `requestGracefulStop` sends one fixed TERM to the still-owned unreaped leader under the existing Session gate and deadline. It retains an attempted request before observation/signalling, refuses repeats and escaped sessions, and leaves waiting/reaping to the existing owner. An accepted request is not proof of application teardown. The standalone deadline-stop fixture covers exact admission boundaries, actual controlled signal/exit, repeated and escaped refusal, injected pre-signal failure and scope-drain interleaving. The fixture child exits immediately in its signal handler; it does not establish Weston or GUI cleanup.

## Persistent application custody

`Warlock.Capture.Process.Persistent` now provides an opaque retained owner and
live-session capability. Startup keeps its original `StartBudget`; an idle live
session can outlast startup without renewing any operation deadline. A lexical
frame admits one action or a bounded request batch of at most16 requests. Entered
failures become Unknown and cannot authorize replay. The first stop request
latches one immutable stop deadline; repeated requests preserve that deadline.
Keep quarantined owners reachable for the trusted supervisor.

Retirement drains admitted callbacks, wake registrations and observation scope
before reaping. If the child exits while process metadata is being read, only the
same owned `ProcessHandle` can supply its exit receipt. Metadata can disappear
before the exit is waitable; the owner waits on that handle within the remaining
original stop deadline, sends no signal on that path, and checks time afterward.
Unconfirmed or late exits remain Unknown with retained custody.

The protected focused check passes the original25-owner controls,32 seeded real
frame/batch lifecycle sequences, two deterministic real-child exit-race cases,
and actual socket callback-drain/once-only-close controls. Thirteen generated
cases exercised the bounded natural-exit wait. The old exit-race failure remains
retained beside the passing fix. Root selects the fixed `--custody` profile
through the existing hash-bound `qa_cpu.py` review; it compiles production and
runs three fixed suites with the pinned fixture. Its report explicitly omits
formal-model and unrelated-suite claims. The full profile remains separate.

See the [current component](../../../../docs/warlock-build-loop/v2/persistent-custody-component-20261102.json)
for source hashes, measured failures and verification scope. Persistent Backend
and retained resolver integration are still being developed. Native presentation,
provider/descendant cleanup, AT/IME, hardware and release acceptance remain open.
