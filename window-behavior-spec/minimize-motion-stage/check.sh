#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
quint typecheck minimize_motion.qnt
quint typecheck minimize_motion_test.qnt
quint test minimize_motion_test.qnt --verbosity 1
quint run minimize_motion.qnt --invariant allProps --max-steps 100 --max-samples 2000 --seed 20260930 --verbosity 1
python3 test_minimize_motion.py
python3 test_motion_core.py
python3 test_motion_service.py
python3 test_native_motion_trial.py
python3 test_windowctl.py
python3 fuzz_desktops.py
node test_motion_qml.js
bash -n hypr-windowctl hypr-windowctl-core
python3 -m py_compile hypr-window-motion
/usr/lib/qt6/bin/qmlformat widget_v62/Windows.qml >/dev/null
/usr/lib/qt6/bin/qmlformat widget_v62/WindowMotion.qml >/dev/null
