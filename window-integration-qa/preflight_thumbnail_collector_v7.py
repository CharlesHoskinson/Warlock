"""Read-only frozen closure/actual imported source observations before GUI."""
import hashlib
import json
import os
from pathlib import Path
import sys

QA=Path('/home/hoskinson/window-integration-qa')
B=QA/'family-preparation-thumbnail-v7'
OUT=QA/'thumbnail-v7-root-frozen-preflight-v1'
OUT.mkdir(mode=0o700)
sys.path.insert(0,str(QA));sys.path.insert(0,str(B))
from qa_launch import require_qa_scope
scope=require_qa_scope()
import native_integration
manifest=B/'frozen-inputs.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(manifest)=='d066ecf9b9ec94f0fe096d117464ba0f611f5b4d655792c0f1f8c6c339cd90eb'
packet=native_integration.verify()
import service_observer
import service_recovery_observer
import module_binding
assert native_integration.SERVICE==service_observer.SERVICE==service_recovery_observer.SERVICE==module_binding.SERVICE
raw=module_binding.capture(OUT/'actual-modules.json','root-frozen-source-preflight')
assert not raw['errors'] and len(raw['modules'])==19 and len(raw['links'])==10 and all(row['matched'] for row in raw['links'])
assert raw['usable'] is False and raw['rawEvidenceOnly'] is True
native_integration.verify()
handoff=json.loads((QA/'thumbnail-v7-crash-handoff-source-audit-v1.json').read_text())
assert all(handoff['fiveChanges'].values())
row={'result':'pass','scope':scope,'manifestSHA256':sha(manifest),'inputs':len(packet['inputs']),'modes':len(packet['inputModes']),'links':len(packet['symlinks']),'serviceManifestSHA256':module_binding.MANIFEST_SHA256,'actualImportedModuleCount':19,'actualClassAndFunctionLinks':10,'sourceObservationOnly':True,'ownerBound':False,'nativeAccepted':False,'fiveHandoffSourceRequirementsReviewed':True,'mainChanged':False,'pythonBytecodePolicy':'PYTHONDONTWRITEBYTECODE=1 inherited by all subprocesses; frozen bytecode inputs remain immutable'}
with (OUT/'preflight.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(row))
