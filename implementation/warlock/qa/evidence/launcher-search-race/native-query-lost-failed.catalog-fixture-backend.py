import importlib.util,json,sys,threading,time
from pathlib import Path
assert Path(sys.argv[1]).read_text()=='{"runtime": "/run/user/1000/wqa/a0fd", "instance": "efb50993780079460b0cbed1363e2166a2de1d9f_1791650819_22198726", "pid": 3425376, "expected_start": 61892204, "binary_sha256": "bae8317a93312ffee6c83d31a38e988c01b4baad80da6e04f4fb160c54517428"}'
sys.path.insert(0,'/home/hoskinson/omarchy-windows-parity/implementation/warlock/adapter')
spec=importlib.util.spec_from_file_location("real_warlock_backend",'/home/hoskinson/omarchy-windows-parity/implementation/warlock/adapter/daemon.py')
daemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon)
sys.argv=[str(spec.origin),'/home/hoskinson/window-integration-qa/warlock-window-feedback-1791650817782866842/search-broker-config.json']
arm=Path('/home/hoskinson/window-integration-qa/warlock-window-feedback-1791650817782866842/race-arm');held=Path('/home/hoskinson/window-integration-qa/warlock-window-feedback-1791650817782866842/race-held.json');release=Path('/home/hoskinson/window-integration-qa/warlock-window-feedback-1791650817782866842/race-release');delivered=Path('/home/hoskinson/window-integration-qa/warlock-window-feedback-1791650817782866842/race-delivered.json')
original_send=daemon.send
stop=threading.Event()
errors=[]
def store(path,frame):
 temp=path.with_suffix(".tmp");temp.write_text(json.dumps(frame));temp.chmod(0o600);temp.replace(path)
def send(frame):
 if frame.get("kind")=="application-catalog" and arm.exists() and not held.exists():
  store(held,frame);return
 original_send(frame)
def delayed():
 try:
  while not stop.wait(.01):
   if release.exists() and held.exists():
    frame=json.loads(held.read_text());original_send(frame);store(delivered,frame);return
 except BaseException as error:errors.append(error)
daemon.send=send
worker=threading.Thread(target=delayed);worker.start()
try:code=daemon.run()
finally:stop.set();worker.join(timeout=2)
assert not worker.is_alive() and not errors
raise SystemExit(code)
