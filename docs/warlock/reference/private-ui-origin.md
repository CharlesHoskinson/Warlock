# Private UI origin boundary

The selected integration is governed by
[the source contract](../../warlock-build-loop/v2/shared-ui-origin-contract-20261101.json)
and [independent minimum readiness](../../warlock-build-loop/v2/ui-origin-readiness-20261101.json).
Implementation and component verification do not establish original ARC024 or
DEL014 acceptance. The latter requires real engine execution-negative reports.

| Owner | Boundary |
| --- | --- |
| Elm DesktopPolicy | Shared pure controller policy for port and HTTP roots. |
| Elm HttpMain/HttpBar/HttpPopup | Static transport interpreters; no simultaneous port adapter or authored JavaScript. |
| Haskell Ui.Policy | Exact origin, role, route, method, header and body admission; CSP and blocking filter description. |
| Haskell Ui.Owner | Three separate loopback listeners, bounded queues and authenticated whole-frame backend transport. |
| Haskell Ui.PrivateNetwork | Same-PID single-identity private network creation and actual native-peer namespace verification; kernel refusal stops startup. |
| Haskell Ui.Display | Only the owning private runtime directory and actual non-symlink owned Wayland Unix socket may supply the two display environment values; no general environment inheritance or compositor authority claim. |
| Haskell Ui.EngineCustody | Early child PID namespace/PID1 lifeline, verified owned pidfd shutdown and bounded exit observation; original UI PID/fd0 remain unchanged. |
| Haskell native WebKit owner | Packaged document loading, actual policy/filter hooks and owned callback/resource lifetime; implementation and verification remain in progress. |

Only `/index.html` is a document route. `/events` requires `X-Warlock-Api: 1`;
the controller can POST `/commit`, and renderer origins can POST `/actions`.
POST requires the exact listener origin, Host including port, content type and
bounded content length. No CORS, arbitrary filesystem mapping, redirects or
browser-selected native event kind is provided. A transport receipt is never a
native operation, presentation disposition or DOM focus acceptance receipt.

The existing bounded backend deadline and retained-batch limit remain unchanged.
This entry point is not yet a persistent desktop service. There is no invented
initial monitor/window snapshot or native-effect grant. DOM focus descriptions
must be interpreted in Elm only after current surface/publication/lease/control
validation and preservation of preedit ownership.

The private SDK pins are build inputs. Loading an engine requires the existing
native gates, complete current source/toolchain custody and actual observation;
the source contract does not authorize a stopped native probe to resume.

The five UI abstractions currently pass152explicitly selected named cases and
six10000-sample campaigns of up to50steps with required positive witnesses.
See `.warlock-contributor/haskell-cpu-1793517625836497642/report.json`.
Actual owning production and selected test builds also pass; original runtime
controls remain separately reported. Failed model/test attempts remain retained.
Provider route and callback retirement are still unqualified in production:
namespace exit or GObject release alone cannot turn engine cleanup into success.

The actual headed Omarchy Chromium renderer fixture passes20checks with2Bar
actions and8Popup actions, current full-width publication/lease strings,
unchanged120/240second bounds, inspected screenshots and owned cleanup. Its raw
receipt is outside Git at
`/home/charl/vm/omarchy/evidence/warlock-ui-origin-20261101/LIVE-ELM-RESULT-20261101.json`.
This fixture does not execute the real Haskell UI owner/backend/Main chain,
establish CSP execution refusal, or qualify native GUI/AT/IME/release obligations.

For this integration's Diátaxis disposition: this reference documents the new
boundary; the existing desktop tutorial and native-run how-to remain unchanged
because no new user deployment or native activation is qualified. The
[implementation observation](../../../wiki/warlock/raw/notes/2026-11-01-private-ui-origin-source.md)
explains the role-isolation decision and current evidence limits. Deployment,
native IME/AT and release instructions require their own later qualification.
