import hashlib,json,os,pathlib,shutil,sys,tempfile,time
from unittest.mock import patch
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from archive import Archive,ArchiveError,Corrupt,Refused,Poisoned,canonical
OUT=ROOT/'qa'/('tests-'+str(time.time_ns()));OUT.mkdir();RESULT=[]
TMP=tempfile.TemporaryDirectory(prefix='elm-archive-647-');BASE=pathlib.Path(TMP.name)
def check(name,condition):
 if not condition:raise AssertionError(name)
 RESULT.append(name)
def raises(name,fn,classes=(ArchiveError,OSError)):
 try:fn()
 except classes:check(name,True);return
 raise AssertionError(name+' did not refuse')
def origin(n,event='Unknown'):
 return {'lifetime':'test-storage-lifetime','session':'1','frontend':'1','protocol':'42','intent':{'requestId':str(n),'generation':str(n),'target':{'address':'0x1','incarnation':'1'}},'event':event}
def raw(n):return ('{ "original" : '+str(n)+', "status": "Unknown", "anchor": "immutable-first" }\n').encode()
def setup(name):
 p=BASE/name;a=Archive(p);a.append(origin(1),'Unknown',raw(1));a.close();return p
started=time.monotonic();metrics={}
try:
 p=BASE/'large';a=Archive(p);first=None
 for n in range(1,1026):
  kind= ['Unknown','Terminal','Prepared','Released','DeliveryAttestation','Predecessor','Admission'][n%7]
  a.append(origin(n,kind),kind,raw(n))
  if n==1:first=a.root_ref.copy()
 check('1025_actual_records_retained',a.root['count']==1025)
 check('history_beyond64_hot_bound',a.max_cache==64 and len(a.cache)<=64)
 check('exact_old_full_origin_bytes',a.lookup(origin(1,'Terminal'))==raw(1))
 check('different_same_target_origin_absent',a.lookup(origin(999999)) is None)
 check('predecessor_root_preserved',(p/first['name']).exists())
 generation=a.root['generation'];quota=dict(a.quota)
 a.append(origin(1,'Terminal'),'Terminal',raw(1));check('exact_idempotency_no_new_generation',a.root['generation']==generation and a.quota==quota)
 raises('immutable_old_outcome_cannot_change',lambda:a.append(origin(1,'Terminal'),'Terminal',b'{"changed":true}'))
 before=a.page_reads;check('paged_lookup_depth_bound',a.lookup(origin(501,'DeliveryAttestation'))==raw(501) and a.page_reads-before<=18)
 pinned=a.batches(23);batch=next(pinned);a.append(origin(1026),'Unknown',raw(1026));count=len(batch)
 for batch in pinned:check('cursor_batch_bound',len(batch)<=23);count+=len(batch)
 check('pinned_generation_excludes_new_append',count==1025)
 check('current_generation_iterates_all',sum(len(b) for b in a.batches())==1026)
 abandoned=a.batches(1);next(abandoned);abandoned.close();check('cancelled_read_cursor_does_not_poison_writer',a.lookup(origin(1,'Terminal'))==raw(1))
 metrics={'retainedRecords':a.root['count'],'cachePages':len(a.cache),'maximumCachePages':a.max_cache,'maximumIndexDepth':16,'maximumCursorBatch':32,'archiveRegularFiles':sum(x.is_file() for x in p.iterdir()),'archiveActualBytes':sum(x.stat().st_size for x in p.iterdir() if x.is_file()),'conservativeQuotaBytes':a.quota['bytes'],'conservativeQuotaFiles':a.quota['files']}
 files_before={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in p.iterdir() if x.name.startswith(('root-','event-'))}
 a.close();events=[];a=Archive(p,hook=events.append)
 check('restart_root_barrier_before_exposure','after:restart-root:fsync' in events)
 check('reopen_exact_unknown_terminal_anchor_payloads',all(a.lookup(origin(n,['Unknown','Terminal','Prepared','Released','DeliveryAttestation','Predecessor','Admission'][n%7]))==raw(n) for n in [1,2,3,4,5,6,64,65,1025]))
 check('original_events_and_predecessors_unchanged',all(hashlib.sha256((p/n).read_bytes()).hexdigest()==h for n,h in files_before.items()))
 raises('second_writer_nonblocking_refusal',lambda:Archive(p),(BlockingIOError,))
 a.close()
 q=setup('quota');a=Archive(q);old=a.root_ref.copy();a.byte_quota=a.quota['bytes']
 raises('quota_refuses_no_eviction',lambda:a.append(origin(2),'Unknown',raw(2)),(Refused,));check('quota_refusal_old_history_usable',a.root_ref==old and a.lookup(origin(1))==raw(1));a.close()
 q=BASE/'independent-evidence';a=Archive(q);evidence={}
 for kind,payload in [('Unknown',b'{ "recordId":"old", "outcome":"Unknown" }\n'),('Terminal',b'{ "recordId":"other", "outcome":"Committed" }\n'),('Prepared',b'{"recordId":"old","proof":{"id":"original-native-proof"},"join":"first"}\n'),('Released',b'{"recordId":"old","id":"original-release-anchor","proof":"original-native-proof"}\n'),('DeliveryAttestation',b'{"recordId":"old","id":"fresh-delivery","anchorId":"original-release-anchor","proof":"different-current-proof"}\n'),('Predecessor',b'{ "schema":6, "originalSourceBytes":"retained-exactly" }\n')]:
  key=origin(80,kind);a.append(key,kind,payload);evidence[kind]=payload
 a.close();a=Archive(q)
 check('independent_unknown_terminal_proof_anchors_exact_on_restart',all(a.lookup(origin(80,k))==payload for k,payload in evidence.items()))
 check('release_or_fresh_delivery_never_overwrites_original_unknown',a.lookup(origin(80,'Unknown'))==evidence['Unknown'] and a.lookup(origin(80,'Prepared'))==evidence['Prepared'] and a.lookup(origin(80,'Released'))==evidence['Released'])
 a.close()
 q=setup('partial');a=Archive(q);actual_write=os.write
 with patch('archive.os.write',side_effect=lambda fd,data:actual_write(fd,data[:7])):a.append(origin(2),'Unknown',raw(2))
 check('real_short_write_loop_preserves_bytes',a.lookup(origin(2))==raw(2));a.close()
 labels=['quota:open','quota:write','quota:fsync','quota:close','quota:rename','quota-dir:fsync','page:open','page:write','page:fsync','page:close','page:rename','pages-dir:fsync','manifest:open','manifest:write','manifest:fsync','manifest:close','manifest:rename','manifest-dir:fsync','current:open','current:write','current:fsync','current:close','current:rename','root:fsync']
 for edge in ['before','after']:
  for label in labels:
   fault=edge+':'+label;q=setup('fault-'+edge+'-'+label.replace(':','-'));a=Archive(q)
   charge=a.quota['files'];seen=[]
   def hook(x):
    seen.append(x)
    if x==fault:raise OSError('injected boundary')
   a.hook=hook
   raises('failure_'+fault,lambda:a.append(origin(2),'Unknown',raw(2)),(OSError,))
   raises('poison_'+fault,lambda:a.lookup(origin(1)),(Poisoned,));a.close()
   order=[];a=Archive(q,hook=order.append);newvisible=label=='root:fsync' or (edge=='after' and label=='current:rename')
   check('restart_conservation_'+fault,a.lookup(origin(1))==raw(1) and (a.lookup(origin(2))==raw(2))==newvisible)
   check('restart_barrier_'+fault,'after:restart-root:fsync' in order)
   check('orphan_charge_no_refund_'+fault,a.quota['files']>=charge)
   a.close()
 # Actual abrupt process exit retains names; parent reopens with fresh locks/barrier.
 for label in ['quota-dir:fsync','pages-dir:fsync','manifest-dir:fsync','current:rename','root:fsync']:
  q=setup('death-'+label.replace(':','-'));pid=os.fork()
  if pid==0:
   a=Archive(q);a.hook=lambda x:os._exit(71) if x=='after:'+label else None;a.append(origin(2),'Unknown',raw(2));os._exit(72)
  _,status=os.waitpid(pid,0);check('actual_process_exit_'+label,os.waitstatus_to_exitcode(status)==71)
  a=Archive(q);check('actual_crash_visible_choice_'+label,a.lookup(origin(1))==raw(1) and (a.lookup(origin(2))==raw(2))==(label in ['current:rename','root:fsync']));a.close()
 q=setup('order');a=Archive(q);order=[];a.hook=order.append;a.append(origin(2),'Unknown',raw(2))
 check('actual_fsync_publication_order',order.index('after:quota-dir:fsync')<order.index('before:page:open')<order.index('after:pages-dir:fsync')<order.index('before:manifest:open')<order.index('after:manifest-dir:fsync')<order.index('before:current:open')<order.index('after:root:fsync'));a.close()
 q=setup('cleanup');a=Archive(q)
 def cleanup_fault(x):
  if x in ['before:page:fsync','before:page:cleanup']:raise OSError('cleanup failure')
 a.hook=cleanup_fault;raises('cleanup_failure_no_ack',lambda:a.append(origin(2),'Unknown',raw(2)),(OSError,));raises('cleanup_failure_poison',lambda:a.lookup(origin(1)),(Poisoned,));a.close();a=Archive(q);check('cleanup_orphan_reopen_conserves_old',a.lookup(origin(1))==raw(1) and a.lookup(origin(2)) is None);a.close()
 q=setup('restart-fsync')
 def restart_fault(x):
  if x=='before:restart-root:fsync':raise OSError('restart barrier failed')
 raises('precall_restart_fsync_refuses_handle',lambda:Archive(q,hook=restart_fault),(OSError,))
 for mutation in ['mode','hardlink','symlink','missing','duplicateJSON','wrongSchema','hash','size','directoryMode','directorySymlink','lockHardlink','quotaBool','markerBool']:
  q=setup('unsafe-'+mutation);a=Archive(q);rootfile=q/a.root_ref['name'];a.close()
  if mutation=='mode':os.chmod(rootfile,0o644)
  elif mutation=='hardlink':os.link(rootfile,q/'alien-link')
  elif mutation=='symlink':rootfile.unlink();rootfile.symlink_to(q/'CURRENT')
  elif mutation=='missing':rootfile.unlink()
  elif mutation=='duplicateJSON':(q/'CURRENT').write_bytes(b'{"schema":1,"schema":1}')
  elif mutation=='wrongSchema':(q/'CURRENT').write_bytes(b'{"schema":2}')
  elif mutation=='hash':rootfile.write_bytes(rootfile.read_bytes().replace(b'"count":1',b'"count":2'))
  elif mutation=='size':rootfile.write_bytes(b'x'*16385)
  elif mutation=='directoryMode':os.chmod(q,0o755)
  elif mutation=='directorySymlink':alias=BASE/'alias';alias.symlink_to(q);q=alias
  elif mutation=='lockHardlink':os.link(q/'WRITER',q/'writer-link')
  elif mutation=='quotaBool':j=json.loads((q/'QUOTA').read_bytes());j['files']=True;(q/'QUOTA').write_bytes(canonical(j))
  elif mutation=='markerBool':j=json.loads((q/'MARKER').read_bytes());j['schema']=True;(q/'MARKER').write_bytes(canonical(j))
  raises('unsafe_'+mutation,lambda:Archive(q))
 q=setup('lazyhash');a=Archive(q);event=next(q.glob('event-*'));event.write_bytes(b'corrupt');raises('lazy_event_hash_refuses_positive_lookup',lambda:a.lookup(origin(1)));raises('lazy_corruption_poison',lambda:a.lookup(origin(999)),(Poisoned,));a.close()
 q=setup('lockreplace');a=Archive(q);(q/'WRITER').unlink();(q/'WRITER').write_bytes(b'');os.chmod(q/'WRITER',0o600);raises('replaced_lock_refuses',lambda:a.lookup(origin(1)));a.close()
 q=setup('invalid');a=Archive(q)
 for data in [b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":1e9999}',b'[]',b'x',b'{"x":"'+b'a'*16384+b'"}']:
  raises('malformed_caller_payload_'+str(len(data)),lambda:a.append(origin(2),'Unknown',data),(Refused,))
 check('caller_refusal_does_not_poison_old_history',a.lookup(origin(1))==raw(1))
 # Typed parser controls isolate decoder branches from content-addressed hash rejection.
 for v in [True,-1,18446744073709551616,'1',1.0]:
  r=dict(a.root_ref);r['size']=v;raises('typed_reference_counter_'+repr(v),lambda r=r:a._check_ref(r),(Corrupt,))
 for node in [{'schema':True,'depth':0,'children':{'0':a.root['index']}},{'schema':1,'depth':True,'children':{'0':a.root['index']}},{'schema':1,'depth':17,'children':{'0':a.root['index']}},{'schema':1,'depth':0,'children':{'xx':a.root['index']}},{'schema':1,'depth':16,'entries':[]},{'schema':1,'depth':16,'entries':[{'keyHash':'0'*64,'event':a.root_ref}]}]:
  raises('typed_index_shape_'+str(len(RESULT)),lambda node=node:a._index(node),(Corrupt,))
 a.close()
 # A failed QUOTA cleanup leaves one fixed slot. Reopening can read old history,
 # but cannot silently delete that slot or accumulate new quota temporaries.
 q=setup('quota-cleanup');a=Archive(q)
 def quota_cleanup_fault(x):
  if x in ['before:quota:fsync','before:quota:cleanup']:raise OSError('quota temporary cleanup failure')
 a.hook=quota_cleanup_fault;raises('quota_cleanup_failure',lambda:a.append(origin(2),'Unknown',raw(2)),(OSError,));a.close()
 slot=q/'.tmp-QUOTA';digest=hashlib.sha256(slot.read_bytes()).hexdigest();a=Archive(q)
 check('quota_orphan_read_reopens_old_root',a.lookup(origin(1))==raw(1))
 raises('quota_fixed_orphan_blocks_new_writer_mutation',lambda:a.append(origin(2),'Unknown',raw(2)),(FileExistsError,));a.close()
 check('quota_orphan_never_deleted_on_failed_exclusive_open',slot.exists() and hashlib.sha256(slot.read_bytes()).hexdigest()==digest)
 check('quota_orphan_bounded_single_slot',len(list(q.glob('.tmp-QUOTA')))==1)
 # Actual visible candidate with correct name/hash but invalid generation type
 # must fail schema validation rather than falling back to predecessor.
 q=setup('validhash-invalid-root');current=json.loads((q/'CURRENT').read_bytes());oldfile=q/current['root']['name'];root=json.loads(oldfile.read_bytes());root['generation']=True
 from archive import ref
 encoded=canonical(root);rr=ref(encoded,'root');(q/rr['name']).write_bytes(encoded);os.chmod(q/rr['name'],0o600);current['root']=rr;(q/'CURRENT').write_bytes(canonical(current))
 raises('correct_hash_bad_root_counter_no_fallback',lambda:Archive(q),(Corrupt,))
 # Actual disk-full write refusal is injected at the syscall; no claimed disk
 # capacity reservation, power-loss or device-level fault qualification.
 q=setup('enospc');a=Archive(q);actual_write=os.write
 def no_space(fd,data):raise OSError(28,'No space left on device')
 with patch('archive.os.write',side_effect=no_space):raises('enospc_no_ack',lambda:a.append(origin(2),'Unknown',raw(2)),(OSError,))
 raises('enospc_writer_poison',lambda:a.lookup(origin(1)),(Poisoned,));a.close();a=Archive(q);check('enospc_reopen_old_exact_record',a.lookup(origin(1))==raw(1));a.close()
 passed=True
except BaseException:
 import traceback
 (OUT/'failure.log').write_text(traceback.format_exc());print(traceback.format_exc());passed=False
finally:
 report={'passed':passed,'assertions':len(RESULT),'checks':RESULT,'elapsedSeconds':time.monotonic()-started,'measuredLargeArchive':metrics,'nativeAcceptance':False,'ledgerIntegrated':False,'powerLossQualified':False,'sourceSHA256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'adapter/archive.py',ROOT/'spec/storage.qnt',ROOT/'spec/REFINEMENT.md',pathlib.Path(__file__)]}}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');TMP.cleanup()
sys.exit(0 if passed else 1)
