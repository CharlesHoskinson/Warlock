# Shared batch recovery regression harness

The semantic and post-close runners, workers, fixtures and trace adapters are
copied byte-for-byte from the passing V303 packet. `origins.json` records each
actual input hash and the original passing reports. This packet does not change
scenario identities or reinterpret the original immediate-dispatch failures.

Run the actual stable recovery production source through the protected launcher:

```
PYTHONDONTWRITEBYTECODE=1 python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-shared-batch-semantic-regressions-v108/semantic/qa/replay.py --source /absolute/held/production/source
PYTHONDONTWRITEBYTECODE=1 python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-shared-batch-semantic-regressions-v108/post-close/qa/replay.py --source /absolute/held/production/source
```

These compile the actual production modules and Main/Popup, run all 78 menu,
53 geometry, 21 refresh and 59 post-close cases, and preserve separate byte-exact
older trace results. They exercise controller semantics with synthetic native
facts. Shared batch-disposition ordering, admission uncertainty, multi-output
ownership, actual native retirement and release acceptance require their own
evidence. No run or gate completion is claimed merely by creating this harness.
