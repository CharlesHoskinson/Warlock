"""Record immutable held CPU source and evidence hashes; no native acceptance."""
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1), 'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'qa/held-source-manifest.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if '--verify' in sys.argv:
    row=json.loads(TARGET.read_text())
    for relative,item in row['files'].items():
        path=ROOT/relative
        assert path.is_file() and not path.is_symlink() and sha(path)==item['sha256'] and path.stat().st_size==item['size'],relative
    print(json.dumps({'passed':True,'nativeAcceptance':False,'manifest':str(TARGET)}));raise SystemExit(0)
assert not TARGET.exists(),'Held source manifest is immutable'
replay_path=ROOT/'qa/replay-1791102994003338950/report.json'
mutation_path=ROOT/'qa/mutations-1791103024370625460/report.json'
replay=json.loads(replay_path.read_text());mutation=json.loads(mutation_path.read_text())
assert replay['passed'] and replay['checks']==78 and replay['geometryChecks']['checks']==53 and replay['refreshChecks']['checks']==21
assert mutation['passed'] and len(mutation['mutants'])==6 and all(m['compiled'] and m['killedByNamedOracle'] for m in mutation['mutants'])
for report in [replay,mutation]:
    for relative,digest in report['inputs'].items():assert sha(ROOT/relative)==digest,relative
for report,path in [(replay,replay_path),(mutation,mutation_path)]:
    for relative,digest in report['artifacts'].items():assert sha(path.parent/relative)==digest,relative
parent=json.loads((ROOT/'qa/refresh-upstream.json').read_text())
for relative,digest in parent['files'].items():assert sha(Path(parent['parent'])/relative)==digest,relative
for relative in parent['unchangedSuites']:assert sha(ROOT/relative)==parent['files'][relative],relative
files={}
for path in [ROOT/'elm.json',*sorted((ROOT/'src').glob('*.elm')),*sorted((ROOT/'qa').rglob('*'))]:
    if path==TARGET:continue
    if path.is_file() and not path.is_symlink():files[str(path.relative_to(ROOT))]={'sha256':sha(path),'size':path.stat().st_size}
manifest={'sourceHeld':True,'createdNs':time.time_ns(),'evidenceIntegrityPassed':True,'nativeAcceptance':False,'wholeFeatureAccepted':False,'completedRequirementIds':[],
          'scope':'Pure Elm dual-observation refresh, retained original78+geometry53 and fresh21 cases; six compiled unsafe mutations caught; no broker/native/GUI acceptance',
          'reports':[{'path':str(path.relative_to(ROOT)),'sha256':sha(path)} for path in [replay_path,mutation_path]],'files':files}
with TARGET.open('x') as stream:stream.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'nativeAcceptance':False,'manifest':str(TARGET),'sha256':sha(TARGET),'files':len(files)}))
