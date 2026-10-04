import importlib.util,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/omarchy-windows-parity/implementation/elm-gtk-privileged-helper-drain-v282/qa')
spec=importlib.util.spec_from_file_location('actual_supervisor','/home/hoskinson/omarchy-windows-parity/implementation/elm-gtk-privileged-helper-drain-v282/qa/activation-supervisor.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=m.signal_exact
marker=Path('/home/hoskinson/omarchy-windows-parity/implementation/elm-gtk-privileged-helper-drain-v282/qa/drain-1791149038736869459/privileged-wait/helper.pid')
def injected(row,sig):
 if marker.exists() and row['pid']==int(marker.read_text()):
  if 'privileged-wait'=='repeated-signal-error':raise RuntimeError('injected repeated signal acquisition failure')
  current=m.identity(row['pid']);current.update(effectiveUid=0,savedUid=0,filesystemUid=0,privilegedCredentials=True)
  raise m.PrivilegedSignalRefused(current)
 return original(row,sig)
m.signal_exact=injected
sys.argv=['actual_supervisor','/run/user/1000/wqa/8823/privileged-wait.json','/home/hoskinson/omarchy-windows-parity/implementation/elm-gtk-privileged-helper-drain-v282/qa/drain-1791149038736869459/privileged-wait/journal.jsonl']
sys.exit(m.main())
