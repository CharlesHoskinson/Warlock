"""Exact V21 byte/mode/link closure. Inventory only unless root explicitly freezes."""
import hashlib
import json
import os
from pathlib import Path
import stat

B = Path(__file__).resolve().parent.parent
V20 = B.parent / 'service-readonly-ipc-v20'
BASE = V20 / 'manifest-readonly-ipc-v20.json'
BASE_SHA = 'd3d836eda0e2a25681df4ca80740ca94f8d2084ea1c48f8834293b740122c068'
V5 = Path('/home/hoskinson/window-integration-qa/family-recovery-bootstrap-v5/frozen-inputs.json')
V5_SHA = 'bbd142db7116de7e076df508dcb6d9b57ceda4d6cc5035cec7da6a5867b2e492'
MANIFEST = B / 'manifest-readonly-longevity-v21.json'
CHECKPOINT = B / 'checkpoint-readonly-longevity-v21.json'
HANDOFF = B / 'source-handoff-v21.json'
CHANGED = {'readonly_ipc.py','native_runtime.py','service_runtime.py','test_readonly_ipc.py'}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory():
    inputs = {}; modes = {}; links = {}
    def add(path, expected=None, mode=None):
        path = Path(path)
        if not path.is_absolute(): path=Path('/home/hoskinson')/path
        actual = sha(path); actual_mode = stat.S_IMODE(path.stat().st_mode)
        if expected is not None and actual != expected: raise ValueError('declared bytes replaced: '+str(path))
        if mode is not None and actual_mode != mode: raise ValueError('declared mode replaced: '+str(path))
        for alias in (path,path.resolve()):
            name = str(alias)
            if name in inputs and (inputs[name] != actual or modes[name] != actual_mode):
                raise ValueError('inventory alias conflicts')
            inputs[name] = actual; modes[name] = actual_mode
        for alias in (path,*path.parents):
            if alias.is_symlink(): links[str(alias)] = os.readlink(alias)
    def retain(path, expected, link_key):
        add(path,expected)
        old = json.loads(path.read_text())
        if set(old['inputs']) != set(old['inputModes']): raise ValueError('inherited mode closure incomplete')
        for p,h in old['inputs'].items(): add(p,h,old['inputModes'][p])
        for p,target in old[link_key].items():
            if not Path(p).is_symlink() or os.readlink(p) != target: raise ValueError('inherited link replaced: '+p)
            links[p]=target
        return old
    old = retain(BASE,BASE_SHA,'links')
    retain(V5,V5_SHA,'symlinks')
    inherited = json.loads((B/'inherited-frozen-v20-source.json').read_text())
    sources = inherited.get('sources', inherited.get('files'))
    if sources is None: raise ValueError('complete inherited source map required')
    changed = []
    for name,item in sources.items():
        path = Path(name)
        if not path.is_absolute(): path=B/name
        original = Path(item.get('source',item.get('original',str(V20/path.name))))
        add(original,item['sha256'],item['mode'])
        if stat.S_IMODE(path.stat().st_mode) != item['mode']: raise ValueError('runtime copied mode differs')
        if sha(path) != item['sha256']: changed.append(path.name)
    if set(changed) != CHANGED: raise ValueError('unreviewed inherited runtime/source delta: '+str(changed))
    proof = json.loads((B/'longevity-final-offline-checkpoint.json').read_text())
    if (proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels']) != (357,308,30) or not proof['sourceUnchangedDuringProof']:
        raise ValueError('full current offline gate required')
    for p,h in proof['sourceSHA256'].items(): add(p,h)
    orphan = json.loads((B/'orphan-refined-formal-before-runtime.json').read_text())
    for p,h in orphan['evidence'].items(): add(p,h)
    for path in sorted(B.rglob('*')):
        # Only this derivative's exact root output descriptors are omitted.
        if path.is_file() and '__pycache__' not in path.parts and path not in (MANIFEST,CHECKPOINT): add(path)
    for p,h in inputs.items():
        if sha(p)!=h or stat.S_IMODE(Path(p).stat().st_mode)!=modes[p]: raise ValueError('closure changed during inventory')
    result = {k:old[k] for k in ('pairedManifest','pairedManifestSHA256','pairedNativeSHA256','producerManifest',
                                'producerManifestSHA256','producer','producerSHA256')}
    result.update(version='service-readonly-longevity-v21',baseManifest=str(BASE),baseManifestSHA256=BASE_SHA,
        retainedFailedCollector=str(V5),retainedFailedCollectorSHA256=V5_SHA,
        allFrozenV20InputsPreserved=True,allFailedV5SourceClosurePreserved=True,
        changedExistingSources=sorted(changed),nativeLaunch=False,nativeAccepted=False,mainChanged=False,
        productionDeployed=False,currentUserCancellationAccepted=False,actorLedgerLongevityImplemented=False,
        originalControllerDeadlineUnchanged=True,atomicNativeAndReceiptGuardsUnchanged=True,
        inputs=dict(sorted(inputs.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())))
    return result


def exclusive_json(path, value):
    fd = os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        with os.fdopen(fd,'wb') as stream:
            fd=None;stream.write((json.dumps(value,indent=2)+'\n').encode());stream.flush();os.fsync(stream.fileno())
        directory = os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if fd is not None:os.close(fd)


def main():
    import argparse
    args=argparse.ArgumentParser();args.add_argument('--freeze',action='store_true');options=args.parse_args()
    if MANIFEST.exists() or CHECKPOINT.exists():raise SystemExit('immutable descriptors already exist')
    packet=inventory();handoff=json.loads(HANDOFF.read_text())
    for p,item in handoff['localSources'].items():
        if packet['inputs'].get(p)!=item['sha256'] or packet['inputModes'].get(p)!=item['mode']:
            raise ValueError('source handoff not fully covered: '+p)
    if options.freeze:
        exclusive_json(MANIFEST,packet)
        exclusive_json(CHECKPOINT,{'manifest':str(MANIFEST),'manifestSHA256':sha(MANIFEST),
            'sourceHandoffSHA256':sha(HANDOFF),'inputCount':len(packet['inputs']),'modeCount':len(packet['inputModes']),
            'linkCount':len(packet['links']),'offlineSHA256':sha(B/'longevity-final-offline-checkpoint.json'),
            'nativeAccepted':False,'currentStageFrozen':True})
    print(json.dumps({'freeze':options.freeze,'inputs':len(packet['inputs']),'modes':len(packet['inputModes']),
                      'links':len(packet['links']),'sourceHandoffSHA256':sha(HANDOFF),
                      'manifestSHA256':sha(MANIFEST) if options.freeze else None,'nativeLaunch':False}))

if __name__=='__main__':main()
