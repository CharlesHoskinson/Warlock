"""Offline-only service proof. No native/renderer launch or installed mutation."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
MODELS=['family_scene','family_destination','transport_dispatch','family_registry','ingress_context','persistent_atlas','pending_direction','runtime_lifecycle','receipt_visual','native_composition','ipc_guard','actor_resources','family_order','gesture_capture','responsive_preparation','native_recovery','recovery_ownership','helper_closure','recovery_constant','runtime_lease','recovery_cancel','renderer_terminal','reduction_validation_v18','legacy_fixture_ready','retained_family_scope','context_completion_fixture','callback_fixture_completion']
EXPECTED_PYTHON=329
EXPECTED_NAMED=254

def main():
    destination=HERE/'offline-family-checkpoint-v5.json'
    if destination.exists():raise SystemExit('fresh offline report destination required')
    env={k:v for k,v in os.environ.items() if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')}
    sources=sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.qnt','.md'))
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    checks=[]
    commands=[[sys.executable,'-m','unittest','discover','-s','.','-p','test_*.py','-v']]
    for model in MODELS:
        commands.extend([['quint','typecheck',model+'_test.qnt'],['quint','test',model+'_test.qnt','--backend=rust','--seed=2026100115'],['quint','run',model+'.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100115','--verbosity=0']])
    named=0;python_count=0
    for index,command in enumerate(commands):
        output=subprocess.run(command,cwd=HERE,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90)
        log=HERE/f'family-v5-check-{index:02d}.log'
        if log.exists():raise SystemExit('fresh log path required')
        fd=os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w')as stream:stream.write(output.stdout)
        checks.append({'command':command,'exitCode':output.returncode,'log':log.name})
        if output.returncode or 'error:' in output.stdout:raise SystemExit('offline failure: '+log.name)
        if index==0:python_count=int(re.search(r'Ran (\d+) tests',output.stdout)[1])
        elif len(command)>1 and command[1]=='test':named+=int(re.search(r'(\d+) passing',output.stdout)[1])
    if python_count!=EXPECTED_PYTHON or named!=EXPECTED_NAMED:raise SystemExit(f'exact suite counts differ: {python_count}/{named}')
    report={'version':'family-service-reduced-validation-v18-exact-family-offline','productionChanged':False,'nativeLaunch':False,'headlessCpuKernelTests':True,'nativeRecoveryAccepted':False,'staleFamilyCancellationSourceImplemented':True,'currentUserCancellationIngressImplemented':False,'pythonTests':python_count,'quintNamedScenarios':named,'quintModels':len(MODELS),'quintSamplesPerModel':2000,'checks':checks,'sourceSHA256':before,'sourceUnchangedDuringProof':True,'scope':'frozen reviewed V17 inheritance; pending validation receipt retained under reduction; exact old visual cancel binding/ACK then fresh Scene/token and atomic pending context rebind; uncertainty/resources quarantined; source-only unpaired, real native reduced-setting and ordinary baseline campaigns remain pending'}
    if any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=digest for p,digest in before.items()):raise SystemExit('source changed during proof')
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w')as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(f'{python_count} Python tests; {named} named Quint scenarios; {len(MODELS)} models × 2000 samples PASS (offline only)')

if __name__=='__main__':main()
