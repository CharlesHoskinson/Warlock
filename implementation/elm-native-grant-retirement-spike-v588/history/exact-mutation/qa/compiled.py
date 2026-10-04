import pathlib,subprocess,json,time,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('compiled-'+str(time.time_ns()));OUT.mkdir()
header=(ROOT/'native/grant-registry.hpp').read_text();test=(ROOT/'native/test.cpp').read_text()
r={'passed':False,'commands':[],'scope':'Standalone actual C++ helper; no compositor or kernel authentication claim'}
def cmd(label,argv,expected=0):
 p=subprocess.run(argv,cwd=OUT,capture_output=True,text=True,timeout=60)
 (OUT/(label+'.stdout')).write_text(p.stdout);(OUT/(label+'.stderr')).write_text(p.stderr)
 r['commands'].append({'label':label,'argv':list(map(str,argv)),'exit':p.returncode})
 assert p.returncode==expected,(label,p.stdout[-1000:],p.stderr[-1000:]);return p
def build(label,body,sanitize=False):
 d=OUT/label;d.mkdir();(d/'grant-registry.hpp').write_text(body);(d/'test.cpp').write_text(test)
 argv=['g++','-std=c++20','-Wall','-Wextra','-Werror','-pedantic','-O1','-g']
 if sanitize:argv+=['-fsanitize=undefined','-fno-sanitize-recover=all']
 cmd(label+'-compile',argv+[str(d/'test.cpp'),'-o',str(d/'test')]);return d/'test'
try:
 result=cmd('accepted-run',[str(build('accepted',header,True))]);r['compiledResult']=json.loads(result.stdout)
 mutations=[
  ('caller-bypass','if (!callerMatches(peer, callerBinding))','if (false && !callerMatches(peer, callerBinding))'),
  ('lifetime-bypass','if (targetBinding.lifetime != lifetime_)','if (false && targetBinding.lifetime != lifetime_)'),
  ('self-retire','if (targetBinding == callerBinding)','if (false && targetBinding == callerBinding)'),
  ('target-frontend-bypass','if (target->second.binding == targetBinding)','if (target->second.binding.session == targetBinding.session && target->second.binding.lifetime == targetBinding.lifetime)'),
  ('id-exhaustion-bypass','if (lastIssued_ == std::numeric_limits<uint64_t>::max())','if (false && lastIssued_ == std::numeric_limits<uint64_t>::max())'),
  ('frontend-exhaustion-bypass','if (frontend == std::numeric_limits<uint64_t>::max())','if (false && frontend == std::numeric_limits<uint64_t>::max())'),
  ('detach-reset','entries_.erase(target);\n        return true;','entries_.erase(target);\n        lastIssued_ = 0;\n        return true;')]
 for label,before,after in mutations:
  assert header.count(before)==1,(label,header.count(before))
  cmd(label+'-rejected',[str(build(label,header.replace(before,after)))],1)
 r.update(passed=True,typedCompiledMutationControls=len(mutations),sourceSHA256=hashlib.sha256(header.encode()).hexdigest())
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
