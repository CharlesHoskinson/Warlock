# Recovering a shell component offline

`adapter/recovery_profile.py` runs outside Elm using Python and retained local
resources. It makes no network or native window-effect request. Prepare a profile
before trying a component so its compatible preferences survive a host failure.

A reviewed release supplies two command descriptors. Each JSON object contains
exactly `schema: 1`, an `argv` array starting with an absolute executable, an
absolute `cwd`, and `files` mapping the executable and required local resources
to SHA-256. Arguments are passed directly without shell expansion. Hashes are
rechecked before launch. Release review must establish dependency completeness
and predecessor acceptance; an arbitrary descriptor is not an accepted package.

Substitute the absolute profile, descriptor and source state paths below. The
source state is the existing `XDG_STATE_HOME` root containing `warlock/`, usually
`~/.local/state`. Run from the candidate directory.

```sh
python3 -B adapter/recovery_profile.py --profile /absolute/profile prepare \
  --predecessor /absolute/predecessor.json \
  --candidate /absolute/candidate.json --source-state /absolute/state
python3 -B adapter/recovery_profile.py --profile /absolute/profile activate
python3 -B adapter/recovery_profile.py --profile /absolute/profile run
```

Prepare exclusively creates the profile. It takes one validated copy of pins,
appearance, motion and explicit shortcut choices under the production stores'
shared lock. Compatible legacy appearance bytes remain verbatim. Unknown schemas
are refused and preserved. Each route receives separate state. Window journals,
pending operations and grants are never copied. Onboarding is not required.

After the candidate host exits, use a terminal or recovery console:

```sh
python3 -B adapter/recovery_profile.py --profile /absolute/profile rollback
python3 -B adapter/recovery_profile.py --profile /absolute/profile status
python3 -B adapter/recovery_profile.py --profile /absolute/profile run
```

Rollback checks only the retained predecessor and prior preferences. It stages
a fresh compatible state directory and publishes the entire route/state selection
with one atomic rename. It neither starts a host nor contacts the failed candidate.
Changed or incompatible candidate preferences remain in their own directory.
Repeated rollback leaves the selected state unchanged, including later edits.

Run holds the profile lock for the host lifetime. Activation, rollback and a
second launch refuse while it runs; status can observe without changing the
selection. A pre-rename failure keeps the old route. A successful rename followed
by failed directory synchronization reports `Unknown`, exit code 3. Inspect
status to reconcile; do not blindly repeat a host operation. Every launch also
validates and synchronizes a fresh selection observation before starting.

Only the explicitly selected private profile changes. These commands never
restart the compositor, edit `/usr/share/omarchy`, replace desktop configuration,
or recover application connections after a compositor crash. Deployment must
route the component exclusively through this launcher and retire previous
interactive hosts first. Unmanaged hosts cannot be inferred from a profile lock.

Component and private native evidence qualify only their recorded scope. The
accepted Omarchy predecessor, full package, main-session rollback, AT and
independent release review remain separate gates.

On October 29, the installed Omarchy Quickshell predecessor started in a
protected private compositor/session bus with a new private HOME. The observed
menu, workspaces and clock painted, and the retry retired its entire owned
process group without escalation or remaining descendants. This qualifies
guarded startup only. It did not prepare or switch a production recovery
profile, fail the candidate, or exercise offline rollback.

The trial used a stock theme and a private layout derived from packaged
defaults. Named startup helpers were refused independently of asynchronous
configuration loading; system-bus and audio endpoints were private/refusing.
It neither imported the user's customization nor established preference
compatibility. The first run's parent-only shutdown left a child for the
protected host to remove; that failed report and limited bar capture remain
preserved alongside the corrected startup observation.

Command manifests (`profile.json`) have a separate 1,048,576-byte limit.
Selection/control metadata retains its 65,536-byte limit, and preference copies
retain their stricter store bounds. A measured 76,694-byte private profile was
refused by the old shared limit; after the fix, the repeated real preparation
accepts its 76,676-byte manifest with the same four preference baselines. Neither
component was launched by this phase. The conservative resource inventory is
partial and does not establish a complete runnable release package.
Candidate failure, standalone rollback, effective predecessor preferences and
editable draft preservation, conflicting-owner refusal and main-session
deployment remain open. See the
[capacity evidence](qa/evidence/recovery-profile-capacity-20261029/manifest.json). See the [bounded Omarchy evidence](qa/evidence/omarchy-predecessor-startup-20261029/manifest.json).

A later full private profile trial prepares a 77,648-byte manifest and observes
the installed predecessor's nonempty effective clock configuration. After it
stops and selects the candidate, the candidate exits with reported code -6
before UI readiness. The guidance, editable draft, planned failure and rollback
steps are not reached. The first full trial remains failed with clean protected
cleanup; see the [full-trial evidence](qa/evidence/omarchy-profile-full-trial-20261029/manifest.json).
