"""Freeze recovery V15 only after complete offline proof; never launches GUI."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sysconfig

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
V13=BASE/'service-recovery-v14/manifest-recovery-v14.json'
V13_SHA='8aa464f75e6ca12a44efd9098b05483245763416145e2190e8d48d04ca926a0a'
ACCEPTED=Path('/home/hoskinson/window-integration-qa/family-continuous-reversal-v3')
BASELINE_SHA='09ecd52991db0581e1dfb5b777b37a8ae50a925b982be29304193485b8a20aee'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    target=HERE/'manifest-recovery-v15.json';checkpoint=HERE/'checkpoint-recovery-v15.json'
    if target.exists() or checkpoint.exists():raise SystemExit('fresh freeze required')
    inputs={};modes={};links={}
    def add(path,expected=None,mode=None):
        path=Path(os.path.abspath(path));digest=sha(path)
        if expected is not None and digest!=expected:raise SystemExit('immutable source changed: '+str(path))
        if mode is not None and stat.S_IMODE(path.stat().st_mode)!=mode:raise SystemExit('immutable mode changed: '+str(path))
        for name in (path,path.resolve()):inputs[str(name)]=digest;modes[str(name)]=stat.S_IMODE(name.stat().st_mode)
        for name in (path,*path.parents):
            if name.is_symlink():links[str(name)]=os.readlink(name)
    def inherit(path,expected,link_field):
        add(path,expected);packet=json.loads(path.read_text())
        for name,digest in packet['inputs'].items():
            selected=Path(name);selected=selected if selected.is_absolute() else Path('/home/hoskinson')/selected
            add(selected,digest,packet['inputModes'].get(name))
        for name,value in packet[link_field].items():
            selected=Path(name);selected=selected if selected.is_absolute() else Path('/home/hoskinson')/selected
            if os.readlink(selected)!=value:raise SystemExit('immutable link changed: '+name)
            links[str(selected)]=value
        return packet
    inherited=inherit(V13,V13_SHA,'links');add(V13.with_name('checkpoint-recovery-v14.json'))
    baseline=inherit(ACCEPTED/'frozen-inputs.json',BASELINE_SHA,'symlinks')
    for path in (ACCEPTED/'attempt-1').rglob('*'):
        if path.is_file():add(path)
    for path in (ACCEPTED/'root-source-review-v3.json',):add(path)
    # New process APIs and fixtures inherit the exact local Linux UAPI,
    # Python runtime/source, selected helper tools and compiler/runtime closure.
    for path in (Path(sysconfig.get_path('stdlib')),):
        for item in path.rglob('*'):
            if item.is_file() and 'site-packages' not in item.parts:add(item)
    binaries=[Path('/usr/bin/'+name) for name in ('python3','bash','timeout','hyprctl','grim','magick','omarchy-shell','cc','ld')]
    for name in ('cc1','collect2'):
        result=subprocess.run(['/usr/bin/cc','-print-file-name='+name],capture_output=True,text=True,timeout=10)
        selected=Path(result.stdout.strip())
        if result.returncode or not selected.is_absolute() or not selected.is_file():raise SystemExit('exact compiler helper closure unavailable: '+name)
        binaries.append(selected)
    for binary in binaries:
        if not binary.exists():
            raise SystemExit('required closure binary absent: '+str(binary))
        add(binary)
        if binary.read_bytes()[:4]!=b'\x7fELF':continue
        result=subprocess.run(['/usr/bin/ldd',str(binary.resolve())],capture_output=True,text=True,timeout=10)
        if result.returncode:raise SystemExit('runtime closure read failed: '+str(binary))
        for line in result.stdout.splitlines():
            for word in line.split():
                if word.startswith('/') and Path(word).is_file():add(word)
    for name in ('/usr/include/linux/pidfd.h','/usr/include/sys/pidfd.h','/usr/include/linux/seccomp.h','/usr/include/linux/filter.h','/usr/include/linux/sched.h'):
        add(name)
    report=json.loads((HERE/'offline-checkpoint.json').read_text())
    if (report['pythonTests'],report['quintNamedScenarios'],report['quintModels'])!=(288,170,21) or not report['sourceUnchangedDuringProof']:raise SystemExit('complete proof counts/source differ')
    for name,digest in report['sourceSHA256'].items():add(name,digest)
    changed=[];new=[]
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.suffix not in ('.py','.md','.qnt'):continue
        previous=V13.parent/path.name
        if previous.exists() and previous.read_bytes()!=path.read_bytes():
            changed.append(path.name);difference=HERE/(path.name+'.v14-recovery-v15.diff')
            difference.write_text(''.join(difflib.unified_diff(previous.read_text().splitlines(True),path.read_text().splitlines(True),fromfile=str(previous),tofile=str(path))))
        elif not previous.exists():new.append(path.name)
    for path in HERE.rglob('*'):
        if path.is_file():add(path)
    for name,digest in inputs.items():
        if sha(name)!=digest or stat.S_IMODE(Path(name).stat().st_mode)!=modes[name]:raise SystemExit('closure changed before freeze: '+name)
    for name,value in links.items():
        if os.readlink(name)!=value:raise SystemExit('closure link changed before freeze: '+name)
    packet={'scope':'fresh recovery source candidate; native restart/quarantine campaign required','nativeLaunch':False,'headlessCpuKernelTests':True,'nativeAccepted':False,'mainChanged':False,'productionDeployed':False,
        'recoveryBaseManifest':str(V13),'recoveryBaseManifestSHA256':V13_SHA,'allFrozenV14InputsPreserved':True,
        'acceptedBaseline':str(ACCEPTED),'acceptedBaselineManifestSHA256':BASELINE_SHA,'retainedOriginalStrictReversalAndRasterOracles':True,
        'pairedManifest':inherited['pairedManifest'],'pairedManifestSHA256':inherited['pairedManifestSHA256'],'pairedNativeSHA256':inherited['pairedNativeSHA256'],
        'producerManifest':inherited['producerManifest'],'producerManifestSHA256':inherited['producerManifestSHA256'],'producer':inherited['producer'],'producerSHA256':inherited['producerSHA256'],
        'changedExistingSources':changed,'newSemanticSources':new,'staleFamilyCancellationImplemented':True,'currentUserCancellationIngressImplemented':False,'interruptionReducedMotionCancellationIngressImplemented':False,'uncertainNativeCallsQuarantine':True,'legacyUnresolvedJournalsRefused':True,
        'requiredNative':['exact gated keeper/isolated job registrations and complete source closure','ordinary baseline/cache/preview/retirement and original strict interior reversals','service death while gated/presenting followed by old exact group and directory closure','restart from returned member results and repeated recovery crash without re-toggling','definite stale/closed/reused/unmapped whole-family cancellation durably acknowledged before source disposal with no window writes','repeated cancelled restart with new exact lease owner, fresh complete member/native context and normal helper closure','unfinished native export/effect and missing proof quarantine, no success or API bind','all main preservation and complete actual lifecycle/source/mode/link/process/runtime/transport proof'],
        'inputs':dict(sorted(inputs.items())),'inputModes':dict(sorted(modes.items())),'links':dict(sorted(links.items()))}
    target.write_text(json.dumps(packet,indent=2)+'\n')
    checkpoint.write_text(json.dumps({'manifest':str(target),'manifestSHA256':sha(target),'inputCount':len(inputs),'modeCount':len(modes),'linkCount':len(links),'offline':report,'currentStageFrozen':True,'nativeAccepted':False,'mainChanged':False},indent=2)+'\n')
    print(json.dumps({'manifestSHA256':sha(target),'checkpointSHA256':sha(checkpoint),'inputs':len(inputs),'modes':len(modes),'links':len(links)}))

if __name__=='__main__':main()
