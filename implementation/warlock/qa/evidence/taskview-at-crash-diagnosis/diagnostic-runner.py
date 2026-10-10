"""Private diagnostic only: debugger is the fixture's actual process ancestor."""
import json, pathlib, subprocess, hashlib, time, sys
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
original=root/'implementation/warlock/qa/native-taskview-at.py'
out=root/'.warlock-contributor'/('taskview-crash-'+str(time.time_ns()))
out.mkdir(mode=0o700)
request=out/'request.json';ready=out/'attached';worker=out/'worker.py'
source=original.read_text();needle="     taskview_at_snapshot('TaskViewBeforeFilter')"
assert source.count(needle)==1
addition='''     report['debuggerDiagnosticOnly']=True
     process_parents={}
     for process_dir in pathlib.Path('/proc').iterdir():
      if not process_dir.name.isdigit():continue
      try:
       status=(process_dir/'status').read_text();parent=int(next(line.split()[1] for line in status.splitlines() if line.startswith('PPid:')))
       process_parents[int(process_dir.name)]=parent
      except (OSError,StopIteration,ValueError):pass
     def owned_descendant(pid):
      visited=set()
      while pid in process_parents and pid not in visited:
       visited.add(pid);pid=process_parents[pid]
       if pid==web.pid:return True
      return False
     web_processes=[]
     for pid in process_parents:
      if not owned_descendant(pid):continue
      try:
       process_dir=pathlib.Path('/proc')/str(pid);argv=(process_dir/'cmdline').read_bytes().split(bytes([0]))
       if argv and pathlib.Path(argv[0].decode()).name=='WebKitWebProcess':
        assert process_dir.stat().st_uid==os.getuid();web_processes.append(pid)
      except (OSError,UnicodeError):pass
     assert len(web_processes)==1,web_processes
     request=pathlib.Path(DIAGNOSTIC_REQUEST);request.write_text(json.dumps({'pid':web_processes[0],'hostPid':web.pid}));request.chmod(0o600)
     wait(lambda:pathlib.Path(DIAGNOSTIC_READY).exists())
'''
source=source.replace(needle,needle+'\n'+addition)
worker.write_text('DIAGNOSTIC_REQUEST='+repr(str(request))+'\nDIAGNOSTIC_READY='+repr(str(ready))+'\n'+source.replace("exec(compile(source, str(p), 'exec'), {'__name__': '__main__', '__file__': __file__, 'taskview_at_inputs': inputs})", "exec(compile(source, str(p), 'exec'), {'__name__': '__main__', '__file__': __file__, 'taskview_at_inputs': inputs, 'DIAGNOSTIC_REQUEST': DIAGNOSTIC_REQUEST, 'DIAGNOSTIC_READY': DIAGNOSTIC_READY})"))
# Preserve the original source-root resolution; diagnostic transformed bytes are
# separately retained and hashed, and never asserted to be the original runner.
entry=out/'entry.py';entry.write_text('exec(compile('+repr(worker.read_text())+','+repr(str(original))+",'exec'),{'__name__':'__main__','__file__':"+repr(str(original))+"})\n")
commands=out/'debug.gdb'
commands.write_text('''set pagination off
set confirm off
set debuginfod enabled off
set sysroot /
file /usr/lib/webkit2gtk-4.1/WebKitWebProcess
set print frame-arguments none
python
import subprocess,time,json,pathlib,gdb
child=subprocess.Popen(['/usr/bin/python3','-B',ENTRY])
deadline=time.monotonic()+20
while not pathlib.Path(REQUEST).exists() and child.poll() is None and time.monotonic()<deadline:time.sleep(.05)
assert pathlib.Path(REQUEST).exists(),('No live diagnostic target',child.poll())
target=json.loads(pathlib.Path(REQUEST).read_text())
gdb.execute('attach '+str(target['pid']))
pathlib.Path(READY).write_text('attached')
gdb.execute('continue')
gdb.execute('info sharedlibrary')
gdb.execute('thread apply all bt 24')
gdb.execute('detach')
child.wait(timeout=35)
pathlib.Path(RESULT).write_text(json.dumps({'fixtureExitCode':child.returncode,'diagnosticOnly':True,'nativeAcceptance':False}))
end
'''.replace('ENTRY',repr(str(entry))).replace('REQUEST',repr(str(request))).replace('READY',repr(str(ready))).replace('RESULT',repr(str(out/'result.json'))))
meta={'diagnosticOnly':True,'nativeAcceptance':False,'originalRunner':str(original),'originalRunnerSHA256':hashlib.sha256(original.read_bytes()).hexdigest(),'transformedWorkerSHA256':hashlib.sha256(worker.read_bytes()).hexdigest(),'debugCommandsSHA256':hashlib.sha256(commands.read_bytes()).hexdigest(),'coreLimitChanged':False,'ptraceSettingChanged':False}
(out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps({'diagnosticDirectory':str(out)}),flush=True)
with (out/'gdb.log').open('w') as stream:
 result=subprocess.run(['/usr/bin/gdb','-nx','--batch','-x',str(commands)],stdout=stream,stderr=subprocess.STDOUT)
print(json.dumps({'gdbExitCode':result.returncode,'result':json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else None,'log':str(out/'gdb.log')}))
sys.exit(result.returncode or 1)
