# Prepare protected verification for a selected change

Use this guide after source ownership and the original oracle are clear. It prepares a reviewable verification plan; commands that compile or run the application execute only through the authorized serialized protected launcher.

## Match the check to the claim

- Changed Elm entry points must compile with the reviewed compiler/cache. Exercise the real production reducer/port/decoder route, not a copied toy implementation.
- Changed native units must compile and relink with reviewed source, dependency, provider and ABI identities. A retained object is reusable only when its actual consumed-input provenance still applies.
- Add a meaningful valid control and an invalid, stale, duplicate or lifecycle schedule relevant to the change. Property/sequence fuzzing records seed, budget, tool/generator/source versions and retained failures. Do not claim a fuzz runner installed merely because policy mentions one.
- Native, physical, keyboard, AT/IME, performance and deployment claims require their original observations. Where an original explicitly permits a bridge, use that permission without inventing a GUI prerequisite.

The contributor plugin's `verify-plan --selected` suggests checks and executes nothing. Review its output and all actual runner/tuple bytes before execution.

## Use the reviewed launchers

For native QA, from the repository root and with your owned participant record:

```sh
python3 -B docs/warlock-build-loop/v2/loop.py   --record .warlock-contributor/your-slice.json   native --runner /absolute/reviewed/runner.py
```

The loop checks the contributor contract before and after and delegates to the pinned serialized native coordinator. It is not an installer and does not make an old runner's absolute paths or tuple current.

For an authorized CPU/compiler check on this host, the protected launcher is in the checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B   /home/charles/Warlock/window-integration-qa/qa_run.py --   /usr/bin/python3 -B /absolute/reviewed/check.py
```

This is a machine-specific invocation, not a portable command or permission to bypass root's team execution ownership. Other machines need a reviewed equivalent launcher and actual tool/input closure. Historical docs contain `/home/hoskinson/...` paths; do not rewrite frozen evidence or assume those paths exist here.

Before the root execution gate, confirm no conflicting QA process, a successful authenticated AgentBus HOLD receipt, exact owning core/plugin/Aquamarine, private runtime/buses, original deadlines, core limit 1 and normal owned cleanup. Preserve the no DRM/XWayland/software fallback rules. Do not activate the main desktop or mutate user drafts to qualify a test.

## Assess and preserve the result

Record exact invocation/source/tool hashes, stdout/stderr and assertion scope. Separate build success, actual behavior, normal exit and teardown. If a harness fails before the intended operation, retain that failure and say the original observation was not reached. Never infer a cause from one generic error or rerun unchanged after a mandatory stop.

For new loader/manifest checks, consume the captured bytes whose hashes were verified. Keep historical source/receipts as historical and explicitly version actual current deltas; do not monkeypatch hashes or relabel old ABI artifacts. A current package lock is not full release acceptance.
