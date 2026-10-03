"""Offline-only service proof. No native/renderer launch or installed mutation."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
MODELS=['family_scene','family_destination','transport_dispatch','family_registry','ingress_context','persistent_atlas','pending_direction','runtime_lifecycle','receipt_visual','native_composition','ipc_guard','actor_resources','family_order','gesture_capture']
EXPECTED_PYTHON=165
EXPECTED_NAMED=90

def main():
    destination=HERE/'offline-checkpoint.json'
    if destination.exists():raise SystemExit('fresh offline report destination required')
    env={k:v for k,v in os.environ.items() if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')}
    checks=[]
    commands=[[sys.executable,'-m','unittest','discover','-s','.','-p','test_*.py','-v']]
    for model in MODELS:
        commands.extend([['quint','typecheck',model+'_test.qnt'],['quint','test',model+'_test.qnt'],['quint','run',model+'.qnt','--invariant=allProps','--max-samples=2000','--max-steps=40','--verbosity=0']])
    named=0;python_count=0
    for index,command in enumerate(commands):
        output=subprocess.run(command,cwd=HERE,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90)
        log=HERE/f'check-{index:02d}.log'
        if log.exists():raise SystemExit('fresh log path required')
        log.write_text(output.stdout)
        checks.append({'command':command,'exitCode':output.returncode,'log':log.name})
        if output.returncode or 'error:' in output.stdout:raise SystemExit('offline failure: '+log.name)
        if index==0:python_count=int(re.search(r'Ran (\d+) tests',output.stdout)[1])
        elif len(command)>1 and command[1]=='test':named+=int(re.search(r'(\d+) passing',output.stdout)[1])
    if python_count!=EXPECTED_PYTHON or named!=EXPECTED_NAMED:raise SystemExit(f'exact suite counts differ: {python_count}/{named}')
    report={'version':'family-service-v12-offline','productionChanged':False,'nativeLaunch':False,'pythonTests':python_count,'quintNamedScenarios':named,'quintModels':len(MODELS),'quintSamplesPerModel':2000,'checks':checks,'scope':'actor bound and normal retirement/shutdown, exact native topological order and ownership-locked gesture retirement; native family/raster/cadence/recovery acceptance remains open'}
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print(f'{python_count} Python tests; {named} named Quint scenarios; {len(MODELS)} models × 2000 samples PASS (offline only)')

if __name__=='__main__':main()
