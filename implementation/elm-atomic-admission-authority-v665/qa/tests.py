import copy,hashlib,json,os,pathlib,sys,tempfile,time
from unittest.mock import patch
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from authority import Authority,counter,COMPLETION_BYTES,COMPLETION_FILES,event_key
from archive_base import Archive,Refused,Corrupt,Poisoned,canonical
O=ROOT/'qa'/('tests-'+str(time.time_ns()));O.mkdir();checks=[]
def check(n,x):
 if not x:raise AssertionError(n)
 checks.append(n)
def refuses(n,f,types=(Refused,Corrupt,OSError)):
 try:f()
 except types:check(n,True);return
 raise AssertionError(n+' did not refuse')
def record(n,request=None,generation=None,session='1',frontend='1'):
 return {'schema':2,'effectProtocol':1,'binding':{'lifetime':'77','session':session,'frontend':frontend},'intent':{'request':str(n if request is None else request),'generation':str(n if generation is None else generation),'incarnation':str(n),'operation':'minimize','context':{'lifetime':'77','epoch':frontend,'output':'1','revision':'1'}},'status':'Pending'}
def raw(n,**kw):return (' \n'+json.dumps(record(n,**kw),indent=1)+'\n').encode()
bound=record(1)['binding']
def check_authority(store,count):
 v=store.readAuthority(bound);check('atomic_count_'+str(count),len(v['admissions'])==count)
 check('reserved_all_live_'+str(count),v['completionReservedBytes']==count*COMPLETION_BYTES and v['completionReservedFiles']==count*COMPLETION_FILES)
 if count:check('independent_maxima_'+str(count),v['request']==str(count) and v['generation']==str(count))
with tempfile.TemporaryDirectory(prefix='elm-aa665-') as temp:
 base=pathlib.Path(temp);path=base/'basic';store=Authority(path,'77')
 check_authority(store,0);old=store.root_ref.copy()
 token=store.commitAdmission(raw(1));check('new_admission_only_after_single_root',token=={'newAdmission':True,'completionReserved':True} and store.root['count']==1 and store.root_ref!=old)
 check_authority(store,1);check('exact_noncanonical_whitespace_bytes_retained',store.readAuthority(bound)['admissions'][0]['exactRecord']==raw(1))
 root=store.root_ref.copy();quota=store.quota.copy();check('duplicate_never_fresh_effect',store.commitAdmission(raw(1))['newAdmission'] is False and store.root_ref==root and store.quota==quota)
 changed=record(1);changed['intent']['operation']='activate';refuses('same_target_changed_full_origin',lambda:store.commitAdmission(canonical(changed)))
 refuses('duplicate_different_exactbytes',lambda:store.commitAdmission(canonical(record(1))))
 refuses('request_stale_generation_fresh',lambda:store.commitAdmission(raw(2,request=1,generation=2)))
 refuses('generation_stale_request_fresh',lambda:store.commitAdmission(raw(2,request=2,generation=1)))
 refuses('opaque_append_forbidden',lambda:store.append({'x':1},'Admission',b'{"x":1}'))
 check('all_prewrites_refusals_unchanged_root',store.root_ref==root and store.quota==quota)
 for n in range(2,20):store.commitAdmission(raw(n))
 check_authority(store,19);check('cache_bounded',store.max_cache<=64)
 snapshot={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in path.iterdir() if p.name.startswith(('event-','root-'))};store.close()
 order=[];store=Authority(path,'77',hook=order.append);check('cold_full_validation_then_root_barrier','after:authority-restart-root:fsync' in order);check_authority(store,19)
 check('old_admission_and_roots_conserved',all(hashlib.sha256((path/n).read_bytes()).hexdigest()==v for n,v in snapshot.items()));store.close()
 refuses('cold_foreign_native_lifetime',lambda:Authority(path,'78'))
 store=Authority(base/'domains','77');store.commitAdmission(raw(1,request=9,generation=2));store.commitAdmission(raw(2,request=10,generation=8));v=store.readAuthority(bound)
 check('request_generation_not_root_count',v['request']=='10' and v['generation']=='8' and store.root['count']==2)
 store.commitAdmission(raw(3,request=1,generation=1,session='2'));b=record(3,session='2')['binding'];check('scope_independent_maxima',store.readAuthority(b)['request']=='1' and store.readAuthority(bound)['request']=='10');store.close()
 for val in [True,1,1.0,'0','01','-1','18446744073709551616','1e2',None]:
  store=Authority(base/('counter-'+str(len(checks))),'77');r=record(1);r['intent']['request']=val
  refuses('typed_counter_'+repr(val),lambda:store.commitAdmission(canonical(r)));check('bad_counter_no_generation',store.root['count']==0);store.close()
 store=Authority(base/'max','77');store.commitAdmission(raw(1,request=18446744073709551615,generation=18446744073709551615));refuses('exhausted_domain_no_next',lambda:store.commitAdmission(raw(2,request=18446744073709551615,generation=18446744073709551615)));store.close()
 store=Authority(base/'quota','77');q=store.quota.copy();store.byte_quota=q['bytes']+COMPLETION_BYTES-1
 refuses('completion_capacity_refuses_before_any_write',lambda:store.commitAdmission(raw(1)));check('quota_refusal_keeps_empty_authority',store.root['count']==0 and store.quota==q);store.close()
 store=Authority(base/'short','77');write=os.write
 with patch('archive_base.os.write',side_effect=lambda fd,data:write(fd,data[:11])):store.commitAdmission(raw(1))
 check('actual_short_writes_exact',store.readAuthority(bound)['admissions'][0]['exactRecord']==raw(1));store.close()
 labels=['quota:open','quota:write','quota:fsync','quota:close','quota:rename','quota-dir:fsync','page:open','page:write','page:fsync','page:close','page:rename','pages-dir:fsync','manifest:open','manifest:write','manifest:fsync','manifest:close','manifest:rename','manifest-dir:fsync','current:open','current:write','current:fsync','current:close','current:rename','root:fsync']
 for edge in ['before','after']:
  for label in labels:
   p=base/('fault-'+edge+'-'+label.replace(':','-'));store=Authority(p,'77');store.commitAdmission(raw(1));fault=edge+':'+label
   def hook(e):
    if e==fault:raise OSError('fault665:'+fault)
   store.hook=hook;refuses('publication_'+fault,lambda:store.commitAdmission(raw(2)),(OSError,));refuses('poison_'+fault,lambda:store.readAuthority(bound),(Poisoned,));store.close()
   order=[];store=Authority(p,'77',hook=order.append);visible=label=='root:fsync' or (edge=='after' and label=='current:rename');check_authority(store,2 if visible else 1)
   check('restart_atomic_'+fault,'after:authority-restart-root:fsync' in order)
   check('original_conserved_'+fault,store.readAuthority(bound)['admissions'][0]['exactRecord']==raw(1));store.close()
 # Independently fault the LAST authority-page publication, not just first event.
 for edge in ['before','after']:
  for label in ['open','write','fsync','close','rename']:
   p=base/('authority-page-'+edge+'-'+label);store=Authority(p,'77');store.commitAdmission(raw(1));opened=[0]
   def last_page(e):
    if e=='before:page:open':opened[0]+=1
    if opened[0]==19 and e==edge+':page:'+label:raise OSError('authority page boundary')
   store.hook=last_page;refuses('last_authority_page_'+edge+':'+label,lambda:store.commitAdmission(raw(2)),(OSError,));store.close()
   store=Authority(p,'77');check_authority(store,1);check('no_partial_maxima_lastpage_'+edge+':'+label,store.lookup(event_key(record(2))) is None);store.close()
 for label in ['quota-dir:fsync','pages-dir:fsync','manifest-dir:fsync','current:rename','root:fsync']:
  p=base/('death-'+label.replace(':','-'));store=Authority(p,'77');store.commitAdmission(raw(1));store.close();pid=os.fork()
  if pid==0:
   child=Authority(p,'77');child.hook=lambda e:os._exit(71) if e=='after:'+label else None;child.commitAdmission(raw(2));os._exit(72)
  _,status=os.waitpid(pid,0);check('actual_process_exit_'+label,os.waitstatus_to_exitcode(status)==71)
  store=Authority(p,'77');check_authority(store,2 if label in ['current:rename','root:fsync'] else 1);store.close()
 def fail(e):
  if e=='before:authority-restart-root:fsync':raise OSError('fresh barrier refused')
 refuses('no_lookup_handle_without_fresh_barrier',lambda:Authority(path,'77',hook=fail),(OSError,))
 # A plain647 nonempty archive is not an authority generation.
 p=base/'non-authority';legacy=Archive(p);legacy.append({'opaque':1},'Admission',b'{"request":"999"}');legacy.close();refuses('incomplete_opaque_transaction_refuses_coldopen',lambda:Authority(p,'77'))
 # Isolated decoder mutations reach typed authority checks without hash mismatch.
 store=Authority(base/'typed','77');store.commitAdmission(raw(1));state=copy.deepcopy(store._state(store.root))
 for name,fn in [('missingReservation',lambda s:s['live'][0].pop('reservedBytes')),('boolReservation',lambda s:s['live'][0].update(reservedFiles=True)),('missingMaxima',lambda s:s['marks'].clear()),('staleGeneration',lambda s:s['marks'][0].update(generation='0')),('inflatedMaxima',lambda s:s['marks'][0].update(request='999')),('foreignScope',lambda s:s['marks'][0]['binding'].update(lifetime='78'))]:
  v=copy.deepcopy(state);fn(v);refuses('typed_authority_'+name,lambda:store._authority(v),(Corrupt,))
 store.close()
report={'passed':True,'assertions':len(checks),'checks':checks,'sourceSHA256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(sorted((ROOT/'adapter').glob('*.py')))+[pathlib.Path(__file__).resolve()]} ,'nativeAcceptance':False,'completionImplemented':False,'CIntegrated':False,'powerLossQualified':False,'S15Accepted':False,'maxNormalLiveAdmissionsMeasured':19,'failureBoundaries':58,'actualAbruptProcessExits':5,'completionBudgetPerOrigin':{'bytes':COMPLETION_BYTES,'files':COMPLETION_FILES}}
(O/'report.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps({'report':str(O/'report.json'),'assertions':len(checks)}))
