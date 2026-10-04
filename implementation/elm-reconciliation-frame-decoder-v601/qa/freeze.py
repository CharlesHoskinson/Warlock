#!/usr/bin/env python3
import hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
primary=max((ROOT/'qa').glob('tests-*/report.json'),key=lambda p:p.parent.name)
mutations=max((ROOT/'qa').glob('mutations-*/report.json'),key=lambda p:p.parent.name)
p=json.loads(primary.read_text());m=json.loads(mutations.read_text())
assert p['passed'] and len(p['checks'])==162 and m['passed'] and len(m['controls'])==5
assert m['primaryCasesSHA256']==sha(primary.parent/'cases.json')
for source in (ROOT/'src').glob('*.elm'):
 assert sha(source)==sha(primary.parent/'inputs/src'/source.name)
 if source.name!='ReconciliationFrame.elm':assert sha(source)==sha(ROOT.parent/'elm-recovery-context-feedback-v592/src'/source.name)
assert sha(ROOT/'qa/Probe.elm')==sha(primary.parent/'inputs/src/Probe.elm')
versions=[]
for command in [['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','--version'],['node','--version'],['/usr/bin/python3','--version']]:
 proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=180);assert proc.returncode==0
 versions.append({'command':command,'exitCode':proc.returncode,'stdout':proc.stdout.decode(),'stderr':proc.stderr.decode()})
(ROOT/'qa/versions.json').write_text(json.dumps(versions,indent=2)+'\n')
files={str(f.relative_to(ROOT)):sha(f) for f in sorted(ROOT.rglob('*')) if f.is_file() and f.name!='component-manifest.json'}
manifest={'schema':1,'component':'elm-reconciliation-frame-decoder-v601','sourceHeld':True,'frozenAtUnixNs':time.time_ns(),'claim':'Isolated pure typed decoding/correlation only','nativeAcceptance':False,'productionWired':False,'durableReleaseAcceptance':False,'primaryReport':str(primary.relative_to(ROOT)),'primaryCases':162,'mutationReport':str(mutations.relative_to(ROOT)),'detectedCompiledMutations':5,'files':files}
(ROOT/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'frozen':True,'files':len(files),'primaryReport':str(primary),'mutationReport':str(mutations),'manifest':str(ROOT/'component-manifest.json')}))
