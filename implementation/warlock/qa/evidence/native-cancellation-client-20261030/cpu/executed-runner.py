#!/usr/bin/env python3
"""Protected focused cancellation-client codec QA; no native load."""
import ast,hashlib,json,os,shutil,subprocess,sys,time,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');P=R/'implementation/warlock';B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.path.insert(0,str(R/'window-integration-qa'))
 from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise RuntimeError('Protected no-argument no-bytecode required')
 out=B/('cancellation-client-'+str(time.time_ns()));out.mkdir(mode=0o700)
 names=['adapter/endpoint.py','adapter/effect_endpoint.py','adapter/cancellation_endpoint.py','qa/check-cancellation-endpoint.py','qa/check-pointer-ownership.py']
 inputs={str(P/n):sha(P/n) for n in names};inputs[str(Path(__file__).resolve())]=sha(__file__)
 report={'passed':False,'nativeAcceptance':False,'transportAuthenticationProved':False,'scope':scope,'inputs':inputs,'commands':[],'sourceBaseRevision':'90d08547e'}
 try:
  for n,h in inputs.items():assert sha(n)==h,n
  work=out/'workspace';(work/'adapter').mkdir(parents=True);(work/'qa').mkdir()
  for n in names:
   body=(P/n).read_bytes();ast.parse(body,filename=str(P/n));(work/n).write_bytes(body)
  report['python']={'path':sys.executable,'sha256':sha(sys.executable),'version':sys.version}
  results={}
  for name in ['check-cancellation-endpoint.py','check-pointer-ownership.py']:
   args=[sys.executable,'-B',str(work/'qa'/name)];stdout=out/(name+'.stdout');stderr=out/(name+'.stderr')
   try:p=subprocess.run(args,cwd=work,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,timeout=30)
   except subprocess.TimeoutExpired as e:
    stdout.write_bytes(e.stdout or b'');stderr.write_bytes(e.stderr or b'');report['commands'].append({'argv':args,'exitCode':None,'timedOut':True});raise
   stdout.write_bytes(p.stdout);stderr.write_bytes(p.stderr);report['commands'].append({'argv':args,'exitCode':p.returncode,'stdoutSHA256':sha(stdout),'stderrSHA256':sha(stderr)})
   if p.returncode:raise RuntimeError(name+' failed; exact diagnostics retained')
   result=json.loads(p.stdout);assert result['passed'];results[name]=result
  assert results['check-cancellation-endpoint.py']['generatedReplyCases']==200 and results['check-cancellation-endpoint.py']['seed']=='0xca11ce01'
  for n,h in inputs.items():assert sha(n)==h,n
  report.update(passed=True,results=results,scopeDescription='Actual new production codec with explicit native response doubles; no native/authenticated transport or durable daemon/UI completion. Existing pointer decoder regression unchanged.')
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 report['outputs']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
