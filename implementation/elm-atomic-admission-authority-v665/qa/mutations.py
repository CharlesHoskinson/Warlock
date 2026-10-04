import hashlib,importlib.util,json,pathlib,subprocess,sys,tempfile,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
r=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'adapter'))
from archive_base import canonical,Refused,Corrupt
if len(sys.argv)>1:
 f=pathlib.Path(sys.argv[1]);case=sys.argv[2];s=importlib.util.spec_from_file_location('mutant_authority',f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 def raw(n,request,generation):return canonical({'schema':2,'effectProtocol':1,'binding':{'lifetime':'77','session':'1','frontend':'1'},'intent':{'request':str(request),'generation':str(generation),'incarnation':str(n),'operation':'minimize','context':{'lifetime':'77','epoch':'1','output':'1','revision':'1'}},'status':'Pending'})
 with tempfile.TemporaryDirectory(prefix='elm-aa665-mutation-') as p:
  a=m.Authority(pathlib.Path(p)/'store','77')
  if case=='skip-generation-domain':
   a.commitAdmission(raw(1,1,1))
   try:a.commitAdmission(raw(2,2,1))
   except Refused:pass
   else:raise AssertionError('stale generation produced newAdmission')
  elif case=='skip-completion-charge':
   before=a.quota.copy();a.commitAdmission(raw(1,1,1))
   assert a.quota['bytes']-before['bytes']>=m.COMPLETION_BYTES,'positive admission lacks charged completion bytes'
  elif case=='skip-cold-authority-barrier':
   a.commitAdmission(raw(1,1,1));a.close();events=[];a=m.Authority(pathlib.Path(p)/'store','77',hook=events.append)
   assert 'after:authority-restart-root:fsync' in events,'usable authority handle exposed without final validated root fsync'
  a.close()
 sys.exit(0)
out=r/'qa'/('mutations-'+str(time.time_ns()));out.mkdir();source=(r/'adapter/authority.py').read_text()
mutations=[('skip-generation-domain'," or int(r['intent']['generation'])<=int(mark['generation'])",''),('skip-completion-charge','+len(root_bytes)+4096+COMPLETION_BYTES','+len(root_bytes)+4096'),('skip-cold-authority-barrier',"self._sync('authority-restart-root')","pass # deliberately skip final validated barrier")]
results=[]
for name,old,new in mutations:
 assert source.count(old)==1,(name,source.count(old));f=out/(name+'.py');f.write_text(source.replace(old,new))
 # Same concrete oracle on original must pass; mutant must produce AssertionError.
 for label,target in [('original',r/'adapter/authority.py'),('mutant',f)]:
  cmd=['/usr/bin/python3','-B',str(r/'qa/mutations.py'),str(target),name];p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(out/(name+'-'+label+'.log')).write_text(p.stdout+p.stderr)
  results.append({'case':name,'version':label,'command':cmd,'exitCode':p.returncode,'specificAssertionFailure':'AssertionError:' in p.stderr,'sourceSHA256':hashlib.sha256(target.read_bytes()).hexdigest()})
v={'passed':all(x['exitCode']==0 if x['version']=='original' else x['exitCode']!=0 and x['specificAssertionFailure'] for x in results),'controls':results,'scope':'actual isolated authority implementation mutations; no native'};(out/'report.json').write_text(json.dumps(v,indent=2)+'\n');print(out/'report.json');sys.exit(0 if v['passed'] else 1)
