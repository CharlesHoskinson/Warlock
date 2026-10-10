import importlib.util,sys
from pathlib import Path
assert Path(sys.argv[1]).read_text()=='{"runtime": "/run/user/1000/wqa/434b", "instance": "efb50993780079460b0cbed1363e2166a2de1d9f_1791652158_1151950593", "pid": 3503275, "expected_start": 62026103, "binary_sha256": "bae8317a93312ffee6c83d31a38e988c01b4baad80da6e04f4fb160c54517428"}'
sys.path.insert(0,'/home/hoskinson/omarchy-windows-parity/implementation/warlock/adapter')
spec=importlib.util.spec_from_file_location("real_warlock_backend",'/home/hoskinson/omarchy-windows-parity/implementation/warlock/adapter/daemon.py')
daemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon)
sys.argv=[str(spec.origin),'/home/hoskinson/window-integration-qa/warlock-window-feedback-1791652156899335138/search-broker-config.json']
original_send=daemon.send
def send(frame):
 original_send(frame)
 if frame.get("kind")=="application-catalog" and frame.get("snapshot") is None:original_send(frame)
daemon.send=send
raise SystemExit(daemon.run())
