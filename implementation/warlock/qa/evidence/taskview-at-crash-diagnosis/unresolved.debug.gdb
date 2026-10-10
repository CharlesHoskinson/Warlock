set pagination off
set confirm off
set debuginfod enabled off
set print frame-arguments none
python
import subprocess,time,json,pathlib,gdb
child=subprocess.Popen(['/usr/bin/python3','-B','/home/hoskinson/omarchy-windows-parity/.warlock-contributor/taskview-crash-1791661773892664957/entry.py'])
deadline=time.monotonic()+20
while not pathlib.Path('/home/hoskinson/omarchy-windows-parity/.warlock-contributor/taskview-crash-1791661773892664957/request.json').exists() and child.poll() is None and time.monotonic()<deadline:time.sleep(.05)
assert pathlib.Path('/home/hoskinson/omarchy-windows-parity/.warlock-contributor/taskview-crash-1791661773892664957/request.json').exists(),('No live diagnostic target',child.poll())
target=json.loads(pathlib.Path('/home/hoskinson/omarchy-windows-parity/.warlock-contributor/taskview-crash-1791661773892664957/request.json').read_text())
gdb.execute('attach '+str(target['pid']))
pathlib.Path('/home/hoskinson/omarchy-windows-parity/.warlock-contributor/taskview-crash-1791661773892664957/attached').write_text('attached')
gdb.execute('continue')
gdb.execute('thread apply all bt 24')
gdb.execute('detach')
child.wait(timeout=35)
pathlib.Path('/home/hoskinson/omarchy-windows-parity/.warlock-contributor/taskview-crash-1791661773892664957/result.json').write_text(json.dumps({'fixtureExitCode':child.returncode,'diagnosticOnly':True,'nativeAcceptance':False}))
end
