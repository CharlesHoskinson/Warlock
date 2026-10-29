set pagination off
set confirm off
set auto-load off
set debuginfod enabled off
set startup-with-shell off
set auto-solib-add on
set print thread-events off
set print frame-arguments none
set backtrace limit 12
handle SIGSTOP nostop noprint pass
handle SIGCONT nostop noprint pass
handle SIGUSR1 nostop noprint pass
handle SIGUSR2 nostop noprint pass
handle SIGPIPE nostop noprint pass
handle SIGTRAP stop print pass
handle SIGSEGV stop print pass
handle SIGABRT stop print pass
handle SIGBUS stop print pass
handle SIGILL stop print pass
handle SIGFPE stop print pass
python
import hashlib,pathlib
path=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-symbols-v1/controller.py')
raw=path.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='c60e5f5675018d389a796863052c735d5b19bf8363cab7892c3377d05b50e7b4'
exec(compile(raw,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
end
quit
