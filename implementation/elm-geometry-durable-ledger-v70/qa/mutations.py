"""Applied unsafe production-module variants killed by external filesystem oracles."""
import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[*sorted((ROOT/'adapter').glob('*.py')),ROOT/'SPEC.md',ROOT/'upstream.json',ROOT/'qa/ledger-test.py',Path(__file__)]
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
source=(ROOT/'adapter/durable_ledger.py').read_text()
variants=[
 ('ignore original binding in receipt key',"['effectProtocol','binding','intent']","['effectProtocol','intent']",'full original binding receipt mismatch session'),
 ('forget Unknown on receipt',"if r['status']=='Unknown':matching[0]['status']='Unknown'","if False:matching[0]['status']='Unknown'",'AUnknown survives B legacy commit'),
 ('evict oldest at capacity',"if len(state['entries'])>=MAX_UNRESOLVED:raise Refused('Ledger unresolved capacity')","if len(state['entries'])>=MAX_UNRESOLVED:state['entries'].pop(0)",'64 full entries persist unknown'),
 ('allow reuse of settled allocation',"int(intent['request'])<=int(m['request']) or int(intent['generation'])<=int(m['generation'])","int(intent['request'])<int(m['request']) or int(intent['generation'])<int(m['generation'])",'one allocation watermark across protocols'),
 ('omit data file fsync',"os.fsync(fd);os.replace(temporary,NAME,src_dir_fd=self.fd,dst_dir_fd=self.fd);os.fsync(self.fd)","os.replace(temporary,NAME,src_dir_fd=self.fd,dst_dir_fd=self.fd);os.fsync(self.fd)",'actual partial writes and EINTR finish')]
checks=[];report={'passed':False,'inputs':inputs,'mutants':checks,'nativeAcceptance':False,'scope':'Actual Python ledger source mutated in private test capsules, real filesystem external oracles; no native host/broker integration'}
try:
 for index,(name,before,after,witness) in enumerate(variants):
  case=OUT/str(index);case.mkdir();(case/'qa').mkdir();shutil.copytree(ROOT/'adapter',case/'adapter')
  for n in ['SPEC.md','upstream.json']:shutil.copy2(ROOT/n,case/n)
  shutil.copy2(ROOT/'qa/ledger-test.py',case/'qa/ledger-test.py')
  assert source.count(before)==1,name
  mutant=source.replace(before,after);compile(mutant,str(case/'adapter/durable_ledger.py'),'exec');(case/'adapter/durable_ledger.py').write_text(mutant)
  run=subprocess.run(['/usr/bin/python3','-B',str(case/'qa/ledger-test.py')],capture_output=True,text=True,timeout=25)
  (case/'stdout').write_text(run.stdout);(case/'stderr').write_text(run.stderr)
  reports=list((case/'qa').glob('ledger-*/report.json'));assert len(reports)==1,name
  p=reports[0];r=json.loads(p.read_text());assert run.returncode!=0 and not r['passed'],name
  failed=[c for c in r['checks'] if not c['passed']];assert len(failed)==1 and witness in failed[0]['name'],(name,failed,r.get('error'))
  assert not any(c['name'].startswith('persisted malformed') for c in failed),'parser fault cannot count as semantic mutation'
  checks.append({'name':name,'caught':True,'witness':failed[0]['name'],'report':str(p.relative_to(OUT)),'reportSHA256':sha(p)})
 for rel,digest in inputs.items():assert sha(ROOT/rel)==digest,rel
 report['passed']=True
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'mutants':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
