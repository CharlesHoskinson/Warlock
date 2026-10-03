"""Root independent source/lock correction review and read-only freeze."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys

QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v23')
OUT=QA/'family-preparation-v23-root-review-v1'
OUT.mkdir(mode=0o700)
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
READY=B/'source-ready-v23.json'
assert sha(READY)=='df126ad3da6c354ddd24ae9834ba2fcd0fb42983012b18f60cba93804d603d27'
ready=json.loads(READY.read_text())
spec=importlib.util.spec_from_file_location('_root_v23_freezer',B/'freeze_staging_preparation.py')
freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
freezer.verify(ready)
assert freezer.inventory()==ready
assert (len(ready['inputs']),len(ready['inputModes']),len(ready['links']))==(15238,15238,158)
assert sha(B/'batch_preview.py')=='875e9e25973458691607503a5293db423b8a6510dfc856f22c99a9121c6037de'
assert sha(B/'native_desktop.py')=='31ace97dda5342519aa749c4dcd01dbd70b425b79b507639a543cf9a2c00ba19'
assert sha(freezer.PROOF)=='b01c57cb72a22d54bbc6bafd96bcedd4fcb76df0635d3b6d5482b58104ad3933'
commands=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
def run(argv,label,cwd=B):
    p=OUT/(label+'.log')
    with p.open('x') as f:
        result=subprocess.run(argv,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=60)
        f.flush();os.fsync(f.fileno())
    commands.append({'argv':argv,'cwd':str(cwd),'exitCode':result.returncode,'log':str(p),'sha256':sha(p)})
    if result.returncode:raise RuntimeError(label+' failed; retained '+str(p))
    return p.read_text()
cpu=run(['/usr/bin/python3','-B','-m','unittest','-v','test_staging_reservation'],'independent-staging-cpu')
assert re.search(r'Ran 9 tests',cpu) and re.search(r'\nOK\s*$',cpu)
freezer.verify(ready)
run(['/usr/bin/python3','-B',str(B/'freeze_staging_preparation.py'),'--freeze'],'freeze',Path('/home/hoskinson'))
run(['/usr/bin/python3','-B',str(B/'freeze_staging_preparation.py'),'--verify'],'verify',Path('/home/hoskinson'))
manifest=B/'manifest-family-preparation-v23.json'
packet=json.loads(manifest.read_text());freezer.verify(packet)
assert {k:v for k,v in packet.items() if k not in ('sourceReady','sourceReadySHA256')}==ready
row={'result':'pass','sourceReadySHA256':sha(READY),'manifest':str(manifest),'manifestSHA256':sha(manifest),'inputs':len(packet['inputs']),'modes':len(packet['inputModes']),'links':len(packet['links']),'independentPythonTests':9,'fullProof':{'pythonTests':359,'named':296,'models':32,'samplesPerModel':2000,'stepsPerSample':100,'sha256':sha(freezer.PROOF)},'soleInheritedProductDelta':'batch_preview.py','exactOtherInheritedSources':133,'reviewedFullContractAndPatchAndNineCases':True,'actualGatedCleanupReceiptReplayReviewed':True,'commands':commands,'scope':{'cgroup':Path('/proc/self/cgroup').read_text().strip(),'coreLimit':1},'nativeAccepted':False,'mainChanged':False}
with (OUT/'review.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({k:row[k] for k in ('result','manifestSHA256','inputs','links','independentPythonTests','nativeAccepted')}))
