"""Mutation check: deliberately unsafe Elm reducers must fail the applied replay checks."""
import hashlib,json,os,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
source=(ROOT/'src/Observer.elm').read_text()
mutations=[
 ('uncorrelated-snapshot','model.binding /= Just binding || model.pending /= Just requestId','model.binding /= Just binding || False'),
 ('foreign-session-delta','if model.binding /= Just binding then','if False then'),
 ('missing-gap-check','UInt64.next (Observation.sequenceCounter old.sequence) /= Just watermark','False'),
 ('obsolete-snapshot','UInt64.compare watermark model.floor /= LT','True'),
 ('delta-clears-barrier','else if model.phase /= Coherent then','else if False then'),
 ('obsolete-response-not-consumed','request { model | phase = Gap, pending = Nothing }','barrier model.floor model')]
rows=[]
for name,old,new in mutations:
 assert source.count(old)==1,(name,source.count(old))
 directory=OUT/name;directory.mkdir();(directory/'src').mkdir()
 shutil.copy2(ROOT/'elm.json',directory/'elm.json')
 for p in (ROOT/'src').glob('*.elm'):shutil.copy2(p,directory/'src'/p.name)
 shutil.copy2(ROOT/'qa/check.cjs',directory/'check.cjs')
 changed=directory/'src/Observer.elm';changed.write_text(source.replace(old,new,1))
 command=['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Replay.elm','--output=replay.js']
 build=subprocess.run(command,cwd=directory,capture_output=True,text=True,timeout=180)
 (directory/'compile.stdout').write_text(build.stdout);(directory/'compile.stderr').write_text(build.stderr)
 assert build.returncode==0,(name,build.stderr)
 env=dict(os.environ,ELM_REPLAY=str(directory/'replay.js'),ELM_REPORT=str(directory/'report.json'),ELM_TRANSCRIPTS=str(directory/'transcripts.json'))
 test=subprocess.run(['node','check.cjs'],cwd=directory,env=env,capture_output=True,text=True,timeout=30)
 (directory/'replay.stdout').write_text(test.stdout);(directory/'replay.stderr').write_text(test.stderr)
 report=json.loads((directory/'report.json').read_text()) if (directory/'report.json').exists() else {}
 failures=[r['name'] for r in report.get('results',[]) if not r['passed']]
 row={'name':name,'compileExit':build.returncode,'replayExit':test.returncode,'actualFailedChecks':failures,'mutationDetected':test.returncode==1 and bool(failures),'mutatedSourceSHA256':hashlib.sha256(changed.read_bytes()).hexdigest()};rows.append(row);print(name,row['mutationDetected'],flush=True)
report={'scope':'Actual compiled Elm mutants; CPU-only regression sensitivity','passed':all(r['mutationDetected'] for r in rows),'sourceSHA256':hashlib.sha256(source.encode()).hexdigest(),'mutations':rows}
report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
