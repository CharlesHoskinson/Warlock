import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
primary=max((ROOT/'qa').glob('tests-*/report.json'),key=lambda p:p.parent.name)
mutants=max((ROOT/'qa').glob('mutations-*/report.json'),key=lambda p:p.parent.name)
build=max((ROOT/'qa').glob('build-*/report.json'),key=lambda p:p.parent.name)
p=json.loads(primary.read_text());m=json.loads(mutants.read_text());b=json.loads(build.read_text())
assert p['passed'] and len(p['checks'])==43 and m['passed'] and len(m['controls'])==9 and b['passed']
for source in (ROOT/'src').glob('*.elm'):
 assert sha(source)==sha(primary.parent/'inputs/src'/source.name)==sha(build.parent/'inputs/src'/source.name)
assert (ROOT/'src/ReconciliationFrame.elm').read_text()==(ROOT.parent/'elm-reconciliation-frame-decoder-v601/src/ReconciliationFrame.elm').read_text().replace('recordDecoder, contextDecoder','proofDecoder, recordDecoder, contextDecoder')
files={str(path.relative_to(ROOT)):sha(path) for path in sorted(ROOT.rglob('*')) if path.is_file() and path.name!='component-manifest.json'}
manifest={'schema':1,'component':ROOT.name,'sourceHeld':True,'frozenAtUnixNs':time.time_ns(),'status':'intermediate-known-liveness-gap','nativeAcceptance':False,'productionWired':False,'finalReconciliationLiveness':False,'primaryReport':str(primary.relative_to(ROOT)),'checks':43,'mutationReport':str(mutants.relative_to(ROOT)),'detectedMutations':9,'buildReport':str(build.relative_to(ROOT)),'files':files}
(ROOT/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'frozen':True,'files':len(files),'manifest':str(ROOT/'component-manifest.json')}))
