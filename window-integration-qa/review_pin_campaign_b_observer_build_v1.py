"""Independent current build/dependency/import review; never loads the observer."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess

B=Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-observer-v2-build')
QA=Path('/home/hoskinson/window-integration-qa')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def command(args):return subprocess.check_output(args,text=True)

def main():
    ready=json.loads((B/'SOURCE_READY.json').read_text())
    assert sha(B/'SOURCE_READY.json')=='e83ea24cb9a5158811012f79b1784b6d9a31bdee738c0a115f186a2c9cafa62d'
    assert sha(ready['inputDescriptor'])==ready['inputDescriptorSHA256']=='0028a9456cddfa02d1daab181dc45e9c543f1d60cffe9b825ac0e6f1dd25d139'
    r=json.loads(Path(ready['inputDescriptor']).read_text())
    assert set(r['inputs'])==set(r['inputModes'])
    for n,d in r['inputs'].items():assert sha(n)==d and stat.S_IMODE(Path(n).stat().st_mode)==r['inputModes'][n]
    for n,t in r['links'].items():assert Path(n).is_symlink() and os.readlink(n)==t
    for n,m in r['directoryModes'].items():assert Path(n).is_dir() and not Path(n).is_symlink() and stat.S_IMODE(Path(n).stat().st_mode)==m
    assert (B/'src/campaign_b_observer.cpp').read_bytes()==(B/'retained-first-build/proposed-source-correction-v2/campaign_b_observer.cpp').read_bytes()
    assert (B/'src/decode_observation.py').read_bytes()==Path('/home/hoskinson/window-behavior-spec/pin-max-native-campaign-b-v1-source-proposal/observer/decode_observation.py').read_bytes()
    for name in ('compile','link'):
        c=json.loads((B/'build'/f'{name}-result.json').read_text());assert c['exitCode']==0
        assert sha(c['log']['resolved'])==c['log']['sha256']
    deps=json.loads((B/'build/dependency-closure.json').read_text())
    actual=shlex.split((B/'build/observer.d').read_text().replace('\\\n',' ').split(':',1)[1])
    assert {str(Path(p).absolute()) for p in actual}==set(deps) and len(deps)==638
    for n,d in deps.items():assert sha(n)==d['sha256'] and oct(stat.S_IMODE(Path(n).stat().st_mode))==d['mode'] and not n.startswith('/usr/include/hyprland/')
    raw=json.loads((B/'build/actual-core-plus-observer-library-closure-v2.json').read_text())
    assert len(raw)==172
    def read_node(n):
        d=raw[n];assert sha(n)==d['metadata']['sha256'] and oct(stat.S_IMODE(Path(n).stat().st_mode))==d['metadata']['mode']
        dynamic=command(['/usr/bin/readelf','-d',n])
        assert re.findall(r'\(NEEDED\).*\[(.+)\]',dynamic)==d['needed']
        assert re.findall(r'\(SONAME\).*\[(.+)\]',dynamic)==d['soname']
        return n,command(['/usr/bin/nm','-D','--defined-only',n])
    exports={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for n,output in pool.map(read_node,raw):
            for line in output.splitlines():
                parts=line.split()
                if len(parts)<3:continue
                sym=parts[-1];exports.setdefault(sym.replace('@@','@'),set()).add(n)
                if '@@' in sym:exports.setdefault(sym.split('@@')[0],set()).add(n)
    imports={};missing=[]
    for line in command(['/usr/bin/nm','-D','--undefined-only',ready['binary']]).splitlines():
        parts=line.split()
        if len(parts)!=2:continue
        binding,sym=parts;providers=exports.get(sym.replace('@@','@'),set())
        imports[sym]={'binding':binding,'providers':providers}
        if binding=='U' and not providers:missing.append(sym)
    declared=json.loads((B/'build/elf-import-closure-v2.json').read_text())
    assert not missing and not declared['unresolvedStrong'] and imports.keys()==declared['imports'].keys()
    for sym,d in imports.items():assert d['binding']==declared['imports'][sym]['binding'] and d['providers']==set(declared['imports'][sym]['providers'])
    assert sum(d['binding']=='U' for d in imports.values())==174
    assert sha(ready['binary'])==ready['binarySHA256']=='3aa57212f976039fdeb89444fb68151231d97f7a41cdfed85b7449e9200f8f42'
    assert ready['observerELFBuildID'] in command(['/usr/bin/readelf','-n',ready['binary']])
    row={'result':'pass','readySHA256':sha(B/'SOURCE_READY.json'),'inputDescriptorSHA256':sha(ready['inputDescriptor']),
         'inputsVerified':len(r['inputs']),'linksVerified':len(r['links']),'directoriesVerified':len(r['directoryModes']),
         'actualCompilerDependenciesVerified':638,'actualLibraryNodesAndSONAMEsVerified':172,'actualVersionedStrongImportsVerified':174,
         'binarySHA256':ready['binarySHA256'],'ELFBuildID':ready['observerELFBuildID'],'approvedSourceCorrectionExact':True,
         'decoderExact':True,'agentFocusedCPU':29,'compileAndLinkNormalZero':True,'initialFailuresPreserved':True,
         'nativeLoaded':False,'liveABIProven':False,'mainChanged':False,'authorization':'build/source component accepted; later root-owned controller freeze/native required',
         'unaccepted':['nativeMAX/pin/normal/exclusive preservation','physical hit/Seat/presentation','scroll/transfer/twooutputs/B24','helper/menu ingress','fullWindowsParity']}
    p=QA/'pin-max-campaign-b-observer-root-build-review-v1.json'
    with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w') as f:
        json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'result':'pass','inputs':len(r['inputs']),'actualImports':174,'reviewSHA256':sha(p)}))

if __name__=='__main__':main()
