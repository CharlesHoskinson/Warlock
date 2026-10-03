"""Transport proof only. Own runtime/bus, no compositor/toolkit/a11y activation."""
import json,os,subprocess,tempfile,time
from pathlib import Path
base=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='keyboard-fence-') as directory:
    runtime=Path(directory);runtime.chmod(0o700)
    env={**os.environ,'XDG_RUNTIME_DIR':str(runtime),'DBUS_SESSION_BUS_ADDRESS':'unix:path='+str(runtime/'bus')}
    env.pop('DBUS_SESSION_BUS_PID',None);env.pop('AT_SPI_BUS_ADDRESS',None)
    daemon=subprocess.Popen(['dbus-daemon','--session','--nofork','--address='+env['DBUS_SESSION_BUS_ADDRESS'],'--print-address'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        address=daemon.stdout.readline().strip();assert address.startswith(env['DBUS_SESSION_BUS_ADDRESS'])
        result=subprocess.run([str(base/'test_actual_dbus')],env=env,text=True,capture_output=True,timeout=15)
        (base/'actual-dbus.log').write_text(result.stdout+result.stderr)
        assert result.returncode==0,result.stderr
        print(result.stdout.strip())
    finally:
        daemon.terminate();daemon.wait(timeout=5)
        (base/'actual-dbus-report.json').write_text(json.dumps(dict(kind='actual extracted v8 functions / real private dbus-daemon transport',pass_=result.returncode==0,daemonPID=daemon.pid,daemonExited=daemon.returncode,runtime=str(runtime),mainBusTouched=False,GUI=False,appVerification=False,cycles=20),indent=2)+'\n')
