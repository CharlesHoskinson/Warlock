# Idempotent stop candidate

Fresh offline stage copied from deployed 6add controller; only shutdown behavior changed. Frozen accepted helper/widget65 are untouched.

`stop` currently raises FileNotFoundError for a service already absent. Candidate returns success only if connection fails before submission and runtime is absent, or it can acquire daemon.lock and prove pending journal is empty with no live PID. It never launches a daemon, clears journal or kills a PID. Busy startup/recovery, nonempty/invalid journal and live PID without listener return error; connected shutdown retains its existing single request/acknowledgement path.

Formal spec was changed before candidate semantics. **4 named stop scenarios / 2000 samples** pass. **7 new actual socket tests + original 3 socket regressions** pass, using isolated fake desktop/runtime and daemon cleanup. No GUI/install performed.

```bash
cd ~/window-behavior-spec/minimize-motion-stage/shutdown-idempotent
python3 test_stop.py
python3 test_motion_service.py
quint test stop_contract_test.qnt --verbosity 1
quint run stop_contract.qnt --invariant allProps --max-samples 2000 --max-steps 100 --verbosity 1
```

Review as a future additive change. Do not replace the accepted frozen helper while root's native matrix is running.
