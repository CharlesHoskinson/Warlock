"""Full inherited service gate plus family preview models; CPU/kernel only."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from check_offline import MODELS as INHERITED_MODELS

HERE=Path(__file__).resolve().parent
MODELS=[*INHERITED_MODELS,'family_preparation','batch_preview_lease','batch_preview_lock','capture_finalization']
EXPECTED_PYTHON=350
EXPECTED_NAMED=280

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_exclusive(path,data):
    with Path(path).open('xb') as output:output.write(data);output.flush();os.fsync(output.fileno())

def main():
    if len(sys.argv)!=2:raise SystemExit('required fresh absolute proof directory')
    destination=Path(sys.argv[1])
    if not destination.is_absolute():raise SystemExit('absolute proof directory required')
    destination.mkdir(mode=0o700)
    env={k:v for k,v in os.environ.items() if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')}
    sources={str(p):{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)} for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.qnt','.md')}
    inherited=json.loads((HERE/'base-v20-source-provenance-v1.json').read_text())
    # The exact original source list includes every inherited test/model/guard.
    original=inherited['copied'];changed=sorted(name for name,h in original.items() if sha(HERE/name)!=h)
    if changed!=['native_desktop.py','scene_controller.py']:raise SystemExit('unreviewed inherited source change: '+repr(changed))
    commands=[[sys.executable,'-m','unittest','discover','-s','.', '-p','test_*.py','-v']]
    for model in MODELS:
        commands.extend([['quint','typecheck',model+'_test.qnt'],['quint','test',model+'_test.qnt','--backend=rust','--seed=20261004'],['quint','run',model+'.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=20261004','--verbosity=0']])
    checks=[];named=0;python_count=0
    for index,command in enumerate(commands):
        result=subprocess.run(command,cwd=HERE,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90)
        log=destination/f'check-{index:02d}.log';write_exclusive(log,result.stdout.encode())
        checks.append({'command':command,'exitCode':result.returncode,'log':str(log),'sha256':sha(log)})
        if result.returncode or 'error:' in result.stdout:
            write_exclusive(destination/'failure.json',json.dumps({'checks':checks,'result':'fail'},indent=2).encode())
            raise SystemExit('CPU/model failure: '+str(log))
        if index==0:python_count=int(re.search(r'Ran (\d+) tests',result.stdout)[1]);print('Python',python_count,'PASS',flush=True)
        elif command[1]=='test':named+=int(re.search(r'(\d+) passing',result.stdout)[1])
        elif command[1]=='run':print(command[2],'2000samples PASS',flush=True)
    actual_names={str(p) for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.qnt','.md')}
    stable=actual_names==set(sources) and all(sha(p)==row['sha256'] and stat.S_IMODE(Path(p).stat().st_mode)==row['mode'] for p,row in sources.items())
    if (python_count,named)!=(EXPECTED_PYTHON,EXPECTED_NAMED) or not stable:raise SystemExit(f'exact counts/source differ: {python_count}/{named}/{stable}')
    report={'result':'pass','pythonTests':python_count,'quintNamedScenarios':named,'quintModels':len(MODELS),'samplesPerModel':2000,'stepsPerSample':100,'sourceUnchangedDuringProof':stable,'sources':sources,'inheritedCount':len(original),'changedInheritedSources':changed,'checks':checks,'nativeAccepted':False,'mainChanged':False,'originalDeadlineSeconds':2,'batchTargetAPISelected':False}
    write_exclusive(destination/'report.json',json.dumps(report,indent=2).encode())
    print(f'{python_count}Python/{named}named/{len(MODELS)}x2000 PASS; native unaccepted')

if __name__=='__main__':main()
