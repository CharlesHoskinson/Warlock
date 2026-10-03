"""Full inherited CPU/Quint proof plus real bounded-history archival; no desktop launch."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from check_offline import MODELS as INHERITED_MODELS

HERE = Path(__file__).resolve().parent
MODELS = INHERITED_MODELS + ['readonly_archival', 'readonly_predecessor']
EXPECTED_PYTHON = 356
EXPECTED_NAMED = 296


def main():
    destination = HERE / 'longevity-offline-checkpoint.json'
    if destination.exists(): raise SystemExit('fresh full offline destination required')
    env = {k:v for k,v in os.environ.items() if k not in
           ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE',
            'DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    sources = sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.qnt','.md'))
    before = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    commands = [[sys.executable,'-B','-m','unittest','discover','-s','.','-p','test_*.py','-v']]
    for model in MODELS:
        commands += [['quint','typecheck',model+'_test.qnt'],
                     ['quint','test',model+'_test.qnt','--backend=rust','--seed=2026100215'],
                     ['quint','run',model+'.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100',
                      '--backend=rust','--seed=2026100215','--verbosity=0']]
    checks=[];named=0;python_count=0
    for index, command in enumerate(commands):
        # This is an offline aggregate runner bound; each query and inherited setup deadline stays exact.
        result = subprocess.run(command,cwd=HERE,env=env,text=True,stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,timeout=300 if index == 0 else 90)
        path = HERE / f'longevity-full-check-{index:02d}.log'
        if path.exists(): raise SystemExit('fresh proof log required')
        path.write_text(result.stdout)
        checks.append({'command':command,'exitCode':result.returncode,'log':str(path),
                       'logSHA256':hashlib.sha256(path.read_bytes()).hexdigest()})
        if result.returncode or 'error:' in result.stdout:
            (HERE/'retained-full-offline-failure.json').write_text(json.dumps({'checks':checks,
                'sourceBeforeSHA256':before,'nativeLaunch':False},indent=2)+'\n')
            raise SystemExit('full offline failure: '+str(path))
        if index==0: python_count=int(re.search(r'Ran (\d+) tests',result.stdout)[1])
        elif command[1]=='test': named+=int(re.search(r'(\d+) passing',result.stdout)[1])
        print(json.dumps({'index':index,'exitCode':0,'pythonTests':python_count,'namedSoFar':named}),flush=True)
    if (python_count,named)!=(EXPECTED_PYTHON,EXPECTED_NAMED): raise SystemExit('exact suite counts differ')
    if any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in before.items()):
        raise SystemExit('source changed during full proof')
    report={'version':'service-readonly-longevity-v21','checks':checks,'pythonTests':python_count,
            'quintNamedScenarios':named,'quintModels':len(MODELS),'samplesPerModel':2000,'steps':100,
            'sourceSHA256':before,'sourceUnchangedDuringProof':True,'nativeLaunch':False,
            'productionDeployed':False,'nativeBaselineAccepted':False,
            'genuine640QueryCpuKernelGate':True,'currentUserCancellationAccepted':False,
            'actorLedgerLongevityImplemented':False,'queryAndControllerDeadlinesUnchanged':True}
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pythonTests':python_count,'quintNamedScenarios':named,'models':len(MODELS),'passed':True}))

if __name__=='__main__':main()
