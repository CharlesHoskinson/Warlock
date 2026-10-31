# Process custody standalone proposal — source-only

Execution by author: NONE. Exact original v13 source and unchanged v12 lease/transfer copies are enumerated in SOURCE-MAP and SHA256SUMS; new facade, tests, fixture and Cabal assembly have separate hashes. No product, public repository or frozen source edited. Root must review Cabal boundary and strict-compile; no new test result claimed. A prior 66-control run is not a result for this assembly.

Root-only proposed commands, in this directory, through the unchanged protected CPU launcher after root source review:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/charles/Warlock/window-integration-qa python3 -B /home/charles/Warlock/window-integration-qa/qa_run.py -- cabal v2-build all --offline --enable-tests --enable-shared --disable-library-vanilla --enable-executable-dynamic --with-hsc2hs=/usr/bin/hsc2hs
```

Root obtains and records `cabal list-bin exe:custody-child`, records the built executable hash before and after, and then runs these exact command shapes through the same protected launcher, substituting that reviewed absolute result for `FIXTURE_PATH`:

```text
cabal v2-test internal-controls --offline --enable-shared --disable-library-vanilla --enable-executable-dynamic --with-hsc2hs=/usr/bin/hsc2hs --test-option=FIXTURE_PATH
cabal v2-test public-controls --offline --enable-shared --disable-library-vanilla --enable-executable-dynamic --with-hsc2hs=/usr/bin/hsc2hs
``` Use bounded owned process-group containment and retain logs/exit status. If the fixture or owner remains live/unsettled on error, fail closed and retain custody; timeout containment is not normal cleanup. Root alone performs these commands and source-bound artifact hashes. Add no package-index downloads. Run `cabal sdist` only after review and independently inspect its archive membership.

The test suite includes meaningful selected controls, not the complete historic 66; guarded close recovery is exercised on the real Owner with no child; post-publication recovery with a live quarantined child is excluded until a real persistent supervisor/contained recovery fixture is available. No issuer or native authority is exposed to untrusted clients. Trusted integration needs a reviewed in-package held-resolver/Pair bridge with exclusive verified descriptor ownership, not an Fd constructor in the public API. Source package does not implement that bridge and cannot establish a selected production lease independently. Native/AT/IME/242/417/release, source provenance and notices remain outstanding.
