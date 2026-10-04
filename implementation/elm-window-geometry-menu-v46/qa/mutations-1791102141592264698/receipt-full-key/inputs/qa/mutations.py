"""Compile actual unsafe Elm derivatives; require external named oracles to fail."""
import hashlib
import json
from pathlib import Path
import resource
import shutil
import subprocess
import time
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1), 'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[ROOT/'elm.json',*sorted((ROOT/'src').glob('*.elm')),*sorted((ROOT/'qa').glob('*.py')),*sorted((ROOT/'qa').glob('*.cjs')),*sorted((ROOT/'qa').glob('*.json'))]
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
mutants=[
('receipt-full-key','src/ReceiptRouter.elm','entry.key==native','entry.key.native==native.native && entry.key.protocol==native.protocol && entry.key.intent.request==native.intent.request','geometry full-key rejects wrong generation'),
('shared-unknown-guard','src/Effects.elm','blocked lifetime incarnation model = List.any','blocked lifetime incarnation model = False && List.any','taskbar-origin Unknown prevents taskbar retry independent of menu ledger'),
('capability-inference','src/Provider.elm','supported op=caps.effects && List.member op caps.operations','supported op=True','unadvertised geometry operations absent preserve legacy two rows')]
report={'passed':False,'nativeAcceptance':False,'inputs':inputs,'mutants':[]}
try:
 for name,relative,needle,replacement,oracle in mutants:
  target=OUT/name;target.mkdir()
  for p in files:
   dest=target/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  source=target/'inputs'/relative;text=source.read_text();assert text.count(needle)==1;source.write_text(text.replace(needle,replacement))
  compile_command=['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/MenuSurfaceReplay.elm','--output='+str(target/'replay.js')]
  process=subprocess.run(compile_command,cwd=target/'inputs',capture_output=True,text=True,timeout=180)
  (target/'compile.stdout').write_text(process.stdout);(target/'compile.stderr').write_text(process.stderr)
  assert process.returncode==0, 'Compile fault is not a killed mutation: '+name
  process=subprocess.run(['node',str(target/'inputs/qa/geometry.cjs'),str(target/'replay.js'),str(target/'inputs/qa/fixtures.json'),str(target/'inputs/qa/geometry-fixtures.json'),str(target/'checks.json')],cwd=target/'inputs',capture_output=True,text=True,timeout=45)
  (target/'checks.stdout').write_text(process.stdout);(target/'checks.stderr').write_text(process.stderr)
  checks=json.loads((target/'checks.json').read_text());failed=[case['name'] for case in checks['cases'] if not case['passed']]
  assert process.returncode==1 and not checks['passed'] and oracle in failed,(name,failed)
  report['mutants'].append({'name':name,'compiled':True,'killedByNamedOracle':oracle,'failedCases':failed,'sourceSHA256':sha(source),'compiledSHA256':sha(target/'replay.js')})
 for relative,digest in inputs.items():assert sha(ROOT/relative)==digest,relative
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json',flush=True)
raise SystemExit(not report['passed'])
