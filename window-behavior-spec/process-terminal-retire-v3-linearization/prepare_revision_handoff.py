from pathlib import Path
import hashlib,json,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
Q=Path('/home/hoskinson/window-integration-qa')
def rec(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
 require_qa_scope()
 ancestor=Q/'process-terminal-retire-v2-source-proposal-handoff-v1.json';a=json.loads(ancestor.read_text())
 assert rec(ancestor)['sha256']=='b9e5117a371161cf12ffa1817cf1c51f01bf19bf140c05101b8449996463825c'
 assert all(rec(Path(p))=={'sha256':h,'mode':a['inputModes'][p]}for p,h in a['inputs'].items())
 proof=B/'formal-linearization-before-source-revision.json';r=json.loads(proof.read_text());assert r['result']=='pass'and '15 passing' in r['commands'][0]['stdout']
 assert all(rec(Path(p))==v for p,v in r['inputs'].items());assert all(c['exitCode']==0 for c in r['commands'])
 inverse=json.loads((B/'proposal/revised-source-inverses.json').read_text());assert inverse['result']=='pass'and all(inverse['checks'].values());assert all(rec(Path(p))==v for p,v in inverse['inputs'].items())
 fixture=json.loads((B/'proposal/future-fixture-source-inverse.json').read_text());assert fixture['result']=='pass'and all(rec(Path(p))==v for p,v in fixture['inputs'].items())
 for p in (B/'proposal/revised-desired').iterdir():
  if p.name not in ['ProcessRegistry.cpp','PinWindowMenu.qml']:assert p.read_bytes()==(B/'proposal/desired'/p.name).read_bytes()
 review=Q/'process-terminal-retire-v2-root-source-review-v1.json';assert rec(review)['sha256']=='348600a1d7f8d1659f2bc5a0982e2f6220f699bba8bf24f4a52873343756a87f'
 files=set(p for p in B.rglob('*')if p.is_file());files.update([ancestor,review]);files.update(Path(p)for p in inverse['inputs']);files.update(Path(p)for p in fixture['inputs']);files.update(Path(v['path'])for v in a['lineage'].values())
 for p in files:assert not p.is_symlink(),p
 inputs={str(p):rec(p)['sha256']for p in sorted(files)};modes={str(p):rec(p)['mode']for p in sorted(files)}
 row={'schema':'process-terminal-retire-source-proposal-v3','status':'revised-source-proposal-ready','inputs':inputs,'inputModes':modes,
      'ancestor':{'path':str(ancestor),**rec(ancestor)},'counterexampleReview':{'path':str(review),**rec(review)},'inheritedLineage':a['lineage'],
      'model':{'path':str(proof),**rec(proof),'named':15,'traces':2000,'steps':100,'beforeSourceRevision':True},'inheritedModels':[41,49],
      'revisionMapping':str(B/'SOURCE_REVISION.md'),'contract':str(B/'LINEARIZATION_CONTRACT.md'),
      'desiredSources':str(B/'proposal/revised-desired'),'narrowRevisionDiffs':str(B/'proposal/v2-to-v3-diffs'),'completeDiffs':str(B/'proposal/revised-diffs'),
      'futureActualDisconnectTest':str(B/'proposal/future-cpu/cpu_retire_product_disconnect.cpp'),
      'original63Exact':True,'originalV7Unchanged':True,'runtimeApplied':False,'compiled':False,'helpersLaunched':False,'futureTestExecuted':False,
      'GUI':False,'nativeReady':False,'installedQS':False,'reliabilityAccepted':False,'sourceReviewBeforeApplicationRequired':True,
      'remaining':['actual Registry fault-at-disconnect and final-admission scheduling proof','current/replaced tuple and visible current/old menu CPU cases','public typed Qt/QML lease and queued signal semantics','one bounded varied unchanged-helper reliability campaign retaining every failure','root-owned private installed-QS/frontend/input proof']}
 target=Q/'process-terminal-retire-v3-source-proposal-handoff-v1.json';assert not target.exists();target.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'packet':str(target),'sha256':rec(target)['sha256'],'inputs':len(inputs),'named':15,'runtimeApplied':False}))
if __name__=='__main__':main()
