"""Freeze fresh responsive V13; no native launch or installed changes."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
OLD=BASE/'service-review-v12'
PAIR=Path('/home/hoskinson/window-integration-qa/toolkit-interruption-v5/frozen-inputs.json')
PAIR_SHA='b5a1363da1f0635ce21e05f961324c246bf31cb914993b798b2ff8eb00909e8a'
GPU=BASE/'producer-production-default-v10/manifest-v10.json'
GPU_SHA='7789616932b896590db95476421c5209484a76842d4e177fb896700e4aadda2a'
RETAINED=Path('/home/hoskinson/window-integration-qa/family-continuous-reversal-v1/attempt-1')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    target=HERE/'manifest-responsive-v13.json';checkpoint=HERE/'checkpoint-responsive-v13.json'
    if target.exists() or checkpoint.exists():raise SystemExit('fresh immutable freeze destination required')
    inputs={};modes={};links={}
    def add(path,expected=None):
        path=Path(os.path.abspath(path));digest=sha(path)
        if expected is not None and digest!=expected:raise SystemExit('immutable input changed: '+str(path))
        for name in (path,path.resolve()):
            inputs[str(name)]=digest;modes[str(name)]=stat.S_IMODE(name.stat().st_mode)
        for name in (path,*path.parents):
            if name.is_symlink():links[str(name)]=os.readlink(name)
    v12=json.loads((OLD/'manifest-v12.json').read_text())
    if len(v12['inputs'])!=1148:raise SystemExit('unexpected V12 closure')
    for name,digest in v12['inputs'].items():add(name,digest)
    add(OLD/'manifest-v12.json');add(OLD/'checkpoint-v12.json')
    for manifest,expected,field in ((PAIR,PAIR_SHA,'files'),(GPU,GPU_SHA,'inputs')):
        add(manifest,expected);packet=json.loads(manifest.read_text())
        for name,digest in packet[field].items():
            name=Path(name);name=name if name.is_absolute() else Path('/home/hoskinson')/name
            add(name,digest)
            recorded=packet['inputModes'].get(str(name))
            if recorded is not None and stat.S_IMODE(name.stat().st_mode)!=recorded:raise SystemExit('inherited mode changed')
        for name,value in packet['links'].items():
            if os.readlink(name)!=value:raise SystemExit('inherited link changed')
        if manifest==GPU:add(manifest.with_name('checkpoint-v10.json'))
    # Retain the strict failed native interior oracle, request times, raw helper
    # archive, all original epochs/retirement and root preservation evidence.
    for path in RETAINED.rglob('*'):
        if path.is_file():add(path)
    report=json.loads((HERE/'offline-checkpoint.json').read_text())
    if (report['pythonTests'],report['quintNamedScenarios'],report['quintModels'])!=(187,98,15) or not report['sourceUnchangedDuringProof']:raise SystemExit('full offline counts/source proof differ')
    for name,digest in report['sourceSHA256'].items():add(name,digest)
    changed=[];new=[]
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.suffix not in ('.py','.md','.qnt'):continue
        before=OLD/path.name
        if before.exists() and path.read_bytes()!=before.read_bytes():
            changed.append(path.name);diff=HERE/(path.name+'.v12-responsive-v13.diff')
            if diff.exists():raise SystemExit('fresh diff required')
            diff.write_text(''.join(difflib.unified_diff(before.read_text().splitlines(True),path.read_text().splitlines(True),fromfile=str(before),tofile=str(path))))
        elif not before.exists():new.append(path.name)
    for path in sorted(HERE.iterdir()):
        if path.is_file():add(path)
    packet={'scope':'fresh responsive preparation candidate; ordinary original interior native reversal acceptance pending','nativeLaunch':False,'mainChanged':False,'productionDeployed':False,
        'original1148V12InputsUnchanged':True,'frozenGPUV10Unchanged':True,'retainedContinuousV1Failure':str(RETAINED),
        'pairedManifest':str(PAIR),'pairedManifestSHA256':PAIR_SHA,'pairedNativeSHA256':json.loads(PAIR.read_text())['binarySHA256'],
        'producerManifest':str(GPU),'producerManifestSHA256':GPU_SHA,'producer':json.loads(GPU.read_text())['binary'],'producerSHA256':json.loads(GPU.read_text())['binarySHA256'],
        'changedExistingSources':changed,'newSemanticSources':new,'atomicNativeEffectsUnchanged':True,'helperRefreshCountUnchanged':True,
        'nativeAccepted':False,'physicalCadenceAccepted':False,'fullWindowsParityAccepted':False,
        'requiredNative':['original baseline family/cache/preview/retirement','original strict two actual interior reversals with real default production renderer','normal exact helper lifetimes','unchanged main source and complete closure/process/transport/private cleanup'],
        'inputs':dict(sorted(inputs.items())),'inputModes':dict(sorted(modes.items())),'links':dict(sorted(links.items()))}
    for name,digest in inputs.items():
        if sha(name)!=digest or stat.S_IMODE(Path(name).stat().st_mode)!=modes[name]:raise SystemExit('closure changed before freeze: '+name)
    for name,value in links.items():
        if os.readlink(name)!=value:raise SystemExit('link changed before freeze: '+name)
    target.write_text(json.dumps(packet,indent=2)+'\n')
    checkpoint.write_text(json.dumps({'manifest':str(target),'manifestSHA256':sha(target),'inputCount':len(inputs),'modeCount':len(modes),'linkCount':len(links),'offline':report,'currentStageFrozen':True,'nativeLaunch':False,'mainChanged':False},indent=2)+'\n')
    print(json.dumps({'manifestSHA256':sha(target),'checkpointSHA256':sha(checkpoint),'inputs':len(inputs),'modes':len(modes),'links':len(links),'changedExistingSources':changed,'newSemanticSources':new}))

if __name__=='__main__':main()
