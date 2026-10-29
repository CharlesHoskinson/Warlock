"""Diagnostic-only derivative, root native-loop launch after supervisor ready."""
import ast,hashlib,os,pathlib,sys
assert os.getuid()==1000 and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1' and sys.argv[1:] in ([],['--at-actions'])
base=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/native-new-instance.py');raw=base.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='9fce62de80ea0f2b57169d79f9806aa1be895fc62dc885b6999ed4e013fafbc1'
tree=ast.parse(raw.decode(),str(base));last=tree.body[-1];assert isinstance(last,ast.Expr) and isinstance(last.value,ast.Call) and isinstance(last.value.func,ast.Name) and last.value.func.id=='exec'
injection=r'''assert source.count("if focus_host:report['focusHostAdaptation']=focus_host")==1
source=source.replace("if focus_host:report['focusHostAdaptation']=focus_host", "report.update(diagnosticOnly=True,instrumented=True,nativeAcceptance=False,fullReleaseAccepted=False)\nif focus_host:report['focusHostAdaptation']=focus_host")
needle="      retire_real_instance(0)\n      enter_pin_keyboard()"
assert source.count(needle)==1
pause=r"""      retire_real_instance(0)
      import stat
      diag=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-symbols-v1')
      def marker(name):
       try:st=(diag/name).lstat()
       except FileNotFoundError:return False
       if not (stat.S_ISREG(st.st_mode) and st.st_uid==1000 and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1):raise RuntimeError('Invalid diagnostic marker')
       return True
      st=diag.lstat();assert stat.S_ISDIR(st.st_mode) and st.st_uid==1000 and stat.S_IMODE(st.st_mode)==0o700 and marker('supervisor-ready')
      packet={'hostPid':web.pid,'hostStart':start_time(web.pid),'cgroup':pathlib.Path('/proc/'+str(web.pid)+'/cgroup').read_text().strip(),'hostSHA256':sha(binary),'sourceRunnerSHA256':'9fce62de80ea0f2b57169d79f9806aa1be895fc62dc885b6999ed4e013fafbc1','instrumented':True,'acceptance':False}
      fd=os.open(diag/'diagnostic-ready.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
      with os.fdopen(fd,'w') as out:json.dump(packet,out);out.flush();os.fsync(out.fileno())
      deadline=time.monotonic()+120
      while not marker('release'):
       if marker('abort'):raise RuntimeError('Diagnostic attach aborted')
       if time.monotonic()>=deadline:raise RuntimeError('Diagnostic attach deadline')
       s.guard();time.sleep(.025)
      if marker('abort'):raise RuntimeError('Diagnostic attach aborted')
      enter_pin_keyboard()"""
source=source.replace(needle,pause)
binding("adapter=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-qa/fresh_candidate.py')", "adapter=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/launcher-pending-source-qualified-v1/fresh_candidate.py')")
binding("assert sha(adapter)=='cb29ebe89b051223037264a366b9616815284b88e3cc452bc18a8993680eb8ab'", "assert sha(adapter)=='9047be2e62947e68621b1bb7fa32403dd930b97cba444d67c82e501a1c4b311f'")
'''
tree.body[-1:-1]=ast.parse(injection).body
exec(compile(ast.fix_missing_locations(tree),str(base),'exec'),{'__name__':'__main__','__file__':str(base)})
