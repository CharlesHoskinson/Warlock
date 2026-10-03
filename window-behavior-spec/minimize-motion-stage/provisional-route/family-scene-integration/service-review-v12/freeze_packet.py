"""Freeze V12 exact source/evidence and reviewed gesture pair, without launch."""
import difflib
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'service-review-v11'
PAIR=Path('/home/hoskinson/window-integration-qa/toolkit-interruption-v4/frozen-inputs.json')
PAIR_SHA='8215d2fd28adfa61b460251c78cb25741906cf91db937d122beb2bba02ec29d6'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    target=HERE/'manifest-v12.json';checkpoint=HERE/'checkpoint-v12.json'
    if target.exists() or checkpoint.exists():raise SystemExit('fresh immutable freeze destination required')
    if sha(PAIR)!=PAIR_SHA:raise SystemExit('reviewed native pair manifest changed')
    inherited=json.loads((OLD/'manifest-v11.json').read_text())['inputs']
    pair={str(Path(name) if Path(name).is_absolute() else Path('/home/hoskinson')/name):value for name,value in json.loads(PAIR.read_text())['files'].items()}
    inputs={**inherited,**pair,str(PAIR):PAIR_SHA,str(OLD/'manifest-v11.json'):sha(OLD/'manifest-v11.json')}
    for name,value in inputs.items():
        if sha(name)!=value:raise SystemExit('inherited reviewed material changed: '+name)
    report=json.loads((HERE/'offline-checkpoint.json').read_text())
    if (report['pythonTests'],report['quintNamedScenarios'],report['quintModels'])!=(165,90,14):raise SystemExit('offline counts differ')
    changed=[];new=[]
    for p in sorted(HERE.iterdir()):
        if not p.is_file() or p.suffix not in ('.py','.md','.qnt') or '.pre-model-' in p.name:continue
        before=OLD/p.name
        if before.exists() and p.read_bytes()!=before.read_bytes():
            changed.append(p.name)
            diff=HERE/(p.name+'.v11-v12.diff')
            if diff.exists():raise SystemExit('fresh diff destination required')
            diff.write_text(''.join(difflib.unified_diff(before.read_text().splitlines(True),p.read_text().splitlines(True),fromfile=str(before),tofile=str(p))))
        elif not before.exists():new.append(p.name)
    for p in sorted(HERE.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:inputs[str(p)]=sha(p)
    packet={'scope':'Offline V12 resource lifecycle/topological native family draw order/ownership-locked gesture retirement; private native integration acceptance pending',
        'productionChanged':False,'nativeLaunch':False,'inputs':inputs,
        'pairedManifest':str(PAIR),'pairedManifestSHA256':PAIR_SHA,
        'pairedNativeSO':str(PAIR.parent/'native-candidate/hyprbars-v20-interruption-candidate.so'),
        'pairedNativeSHA256':json.loads(PAIR.read_text())['binarySHA256'],
        'pairedSnapLua':str(PAIR.parent/'native-candidate/installed-snap.lua'),
        'pairedCloseHelper':'/home/hoskinson/window-integration-qa/snap-close-identity-v1/hypr-snap-groups',
        'changedExistingSources':changed,'newSemanticSources':new,
        'requiredNative':['baseline complete family/topological vector','idle retirement normal actor/renderer/files cleanup','exact minimized shared cache retention and fresh actor restore','paired held gesture retirement without rollback','full-raster strict comparator','receipt reversal without metadata hold','physical 240Hz/cross-output/failure/reduced/recovery']}
    target.write_text(json.dumps(packet,indent=2)+'\n')
    checkpoint.write_text(json.dumps({'manifest':str(target),'manifestSHA256':sha(target),'inputCount':len(inputs),'offline':report,'currentStageFrozen':True,'nativeLaunch':False,'productionChanged':False},indent=2)+'\n')
    print(json.dumps({'manifestSHA256':sha(target),'checkpointSHA256':sha(checkpoint),'inputCount':len(inputs),'changedExistingSources':changed,'newSemanticSources':new}))

if __name__=='__main__':main()
