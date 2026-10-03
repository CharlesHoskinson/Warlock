"""Owned teardown-only QS scheduling barrier; imports never contact a desktop."""
from pathlib import Path
import json,os,re,secrets,time
import helper_observer as observer
import evaluation_setup
from arm_lock import locked_until,remaining
B=Path(__file__).resolve().parent
KINDS={'snapshot','action','capture','allCapture'}
STATE_KEYS={'screenName','currentMonitor','nonce','quiesced','error','queuedActions','queuedBudget','timers','generations','current','processes','records'}
def prepare(env):
 if 'WINDOW_QA_TERMINAL_NONCE' in env:raise RuntimeError('Fresh owned terminal nonce required')
 env['WINDOW_QA_TERMINAL_NONCE']=secrets.token_hex(16)
 return dict(nonce=env['WINDOW_QA_TERMINAL_NONCE'],phase='normal private teardown only',sourceSHA256=observer.digest(__file__))
def unique(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise RuntimeError('Duplicate terminal receipt JSON key')
  result[key]=value
 return result
def integer(value,minimum=0):return type(value)is int and minimum<=value<=8192
def command(value):return isinstance(value,list) and bool(value) and all(isinstance(x,str)and len(x)<=4096 for x in value)and len(value)<=32

def validate(answer,nonce,outputs,prior=None):
 if not isinstance(answer,dict) or set(answer)!={'version','nonce','ack','states'} or type(answer['version'])is not int or answer['version']!=1 or answer['nonce']!=nonce or answer['ack']is not True or not isinstance(answer['states'],list) or not answer['states']:
  raise RuntimeError('Exact acknowledged terminal widget schema required')
 seen=set();drained=True
 for state in answer['states']:
  if not isinstance(state,dict)or set(state)!=STATE_KEYS or not isinstance(state['screenName'],str)or state['screenName']not in outputs or state['screenName']in seen or type(state['currentMonitor'])is not int or state['currentMonitor']!=outputs[state['screenName']]:raise RuntimeError('Terminal output/widget authority changed')
  seen.add(state['screenName'])
  if state['nonce']!=nonce or state['quiesced']is not True or state['error']!='':raise RuntimeError('Terminal marker reported refusal/unknown Process outcome')
  if not integer(state['queuedActions'])or not integer(state['queuedBudget'])or not isinstance(state['timers'],dict)or set(state['timers'])!={'snapshot','capture','allCapture','captureDelay','queueDelay'}or any(type(v)is not bool for v in state['timers'].values()):raise RuntimeError('Unknown terminal queue/timer schema')
  if any(state['timers'][k]for k in ('snapshot','capture','allCapture')):raise RuntimeError('Future terminal scheduling did not stop')
  if not isinstance(state['generations'],dict)or set(state['generations'])!=KINDS or not all(integer(x)for x in state['generations'].values())or not isinstance(state['current'],dict)or not set(state['current'])<=KINDS or not isinstance(state['processes'],dict)or set(state['processes'])!=KINDS or not isinstance(state['records'],list)or len(state['records'])>8192:raise RuntimeError('Unknown actual Process generation schema')
  generations={k:0 for k in KINDS};active={};quiesced=False;old_budget=None;post_actions=0
  for row in state['records']:
   if not isinstance(row,dict)or type(row.get('utcMs'))is not int or row['utcMs']<=0:raise RuntimeError('Unknown Process evidence row')
   event=row.get('event')
   if event=='quiesced':
    if set(row)!={'event','utcMs','nonce','queuedActions'}or quiesced or row['nonce']!=nonce or not integer(row['queuedActions']):raise RuntimeError('Duplicate/changed terminal scheduling epoch')
    quiesced=True;old_budget=row['queuedActions'];continue
   kind=row.get('kind');generation=row.get('generation')
   if kind not in KINDS or not integer(generation,1):raise RuntimeError('Unknown Process receipt lifetime')
   if event=='requested':
    if set(row)!={'event','utcMs','kind','generation','commandDeclaration'}or not command(row['commandDeclaration'])or generation!=generations[kind]+1 or kind in active:raise RuntimeError('Overlapping/malformed Process request')
    if quiesced:
     if kind!='action':raise RuntimeError('Fresh polling/capture request after terminal barrier')
     post_actions+=1
     if post_actions>old_budget:raise RuntimeError('New action beyond original terminal queue')
    generations[kind]=generation;active[kind]=dict(generation=generation,command=row['commandDeclaration'],pid=0,started=False)
   elif event=='started':
    if set(row)!={'event','utcMs','kind','generation','pid','commandDeclarationAtStart'}or kind not in active or active[kind]['generation']!=generation or active[kind]['started']or type(row['pid'])is not int or not 0<row['pid']<2147483648 or not command(row['commandDeclarationAtStart']):raise RuntimeError('Actual Process start differs from exact request')
    active[kind].update(pid=row['pid'],started=True)
   elif event=='exited':
    if set(row)!={'event','utcMs','kind','generation','pid','code','status'}or kind not in active or active[kind]['generation']!=generation or not active[kind]['started']or row['pid']!=active[kind]['pid']or type(row['code'])is not int or type(row['status'])is not int or row['code']!=0 or row['status']!=0:raise RuntimeError('Actual Process normal code/status receipt required')
    del active[kind]
   else:raise RuntimeError('Unknown actual Process terminal event')
  if not quiesced or state['generations']!=generations or state['current']!=active or state['queuedBudget']!=old_budget-post_actions:raise RuntimeError('Process epoch/current/queue evidence differs')
  for kind,p in state['processes'].items():
   if not isinstance(p,dict)or set(p)!={'running','pid','command'}or type(p['running'])is not bool or not command(p['command'])or p['pid']is not None and(type(p['pid'])is not int or not 0<=p['pid']<2147483648):raise RuntimeError('Unknown live Process observation')
   if kind in active:
    a=active[kind]
    if not p['running']or a['started']and p['pid']!=a['pid']:raise RuntimeError('Process request lacks live exact current observation')
   elif p['running']or p['pid']not in (None,0):raise RuntimeError('Unrecorded active Process')
  if prior is not None:
   previous=[x for x in prior['states']if x['screenName']==state['screenName']]
   if len(previous)!=1 or previous[0]['currentMonitor']!=state['currentMonitor']or state['records'][:len(previous[0]['records'])]!=previous[0]['records']:raise RuntimeError('Terminal records/output epoch reset or replaced')
  if active or state['queuedActions']or state['queuedBudget']or any(state['timers'].values()):drained=False
  if generations['snapshot']<1:raise RuntimeError('No genuine snapshot Process evidence')
 if seen!=set(outputs):raise RuntimeError('Missing exact terminal output widget')
 return drained

def service_phase(config,report):
    captured=[row for row in report['processes']if row['role']=='held-service']
    root=config.get('queryRoots',{}).get('service')
    if not captured:
        if root is not None or 'service' in report['cleanup'] or 'serviceEvidenceAcceptance' in report:
            raise RuntimeError('Service absence differs from captured/registered authority')
        return dict(mode='observed no captured or registered service',normalExitNotInferred=True)
    if len(captured)!=1 or root is None or root['identity']!=captured[0]['identity']:
        raise RuntimeError('Exact captured/registered service root differs')
    identity=captured[0]['identity'];cleanup=report['cleanup'].get('service',{})
    if cleanup.get('exitCode')!=0 or cleanup.get('exactOriginalGone')is not True or observer.still_live(identity):
        raise RuntimeError('Exact service normal exit and lifetime gone required before terminal barrier')
    evidence=report.get('serviceEvidenceAcceptance',{})
    if evidence.get('serviceClosed')is not True or evidence.get('allNormal')is not True:
        raise RuntimeError('Actual service renderer/resource normal closure required before terminal barrier')
    return dict(mode='exact captured service normally closed',identity=identity,exitCode=0,actualOriginalGone=True,resourceAcceptance=evidence)

def normal_barrier(lifecycle,env,config,session,report,output,pointer,keyboard):
 nonce=env.get('WINDOW_QA_TERMINAL_NONCE','')
 if not re.fullmatch('[0-9a-f]{32}',nonce):raise RuntimeError('Exact private terminal nonce absent')
 if report.get('featureExecutionEnded')is not True:raise RuntimeError('Terminal barrier cannot run during features')
 for kind,producer in (('pointer',pointer),('keyboard',keyboard)):
  if producer is not None and (report['cleanup'].get(kind,{}).get('normalEOF')is not True or report['cleanup'][kind].get('knownDownTransitionsReleased')is not True or producer.down):raise RuntimeError('Genuine normal input release/EOF required before terminal barrier')
 for case in report['cases']:
  if case.get('processIdentity')and(case['cleanup'].get('normalPublicQuit')is not True or case['cleanup'].get('fixtureExitCode')!=0 or observer.still_live(case['processIdentity'])):raise RuntimeError('Exact public fixture normal lifetime closure required before terminal barrier')
 service_proof=service_phase(config,report)
 if session.data('clients'):raise RuntimeError('Actual owned client list not empty before terminal barrier')
 outputs={row['name']:row['id']for row in session.data('monitors')}
 if not outputs or len(outputs)!=len(session.data('monitors')):raise RuntimeError('Exact current output set required')
 deadline=time.monotonic()+8;record=dict(nonce=nonce,qsIdentity=lifecycle.identity,featureResult=report['result'],budgetSeconds=8,samples=[],controlCalls=[],servicePhaseProof=service_proof,accepted=False)
 expected={}
 for rel in ('home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml','home/.config/omarchy/plugins/hoskinson.windows/widget_v65/TaskbarPopup.qml'):
  source=B/'payload'/rel;actual=Path(env['HOME'])/Path(rel).relative_to('home');expected[rel]=dict(source=observer.material_witness(source),actual=observer.material_witness(actual))
  if expected[rel]['source']['sha256']!=expected[rel]['actual']['sha256']:raise RuntimeError('Exact private terminal QML bytes differ')
 def guard():
  remaining(deadline);lifecycle.guard()
  if not lifecycle.ready or config['queryRoots']['qs']['identity']!=lifecycle.identity:raise RuntimeError('Exact ready registered QS lifetime required')
  values=dict(x.split(b'=',1)for x in(Path('/proc')/str(lifecycle.identity['pid'])/'environ').read_bytes().split(b'\0')if b'='in x)
  if values.get(b'WINDOW_QA_TERMINAL_NONCE')!=nonce.encode():raise RuntimeError('Exact QS terminal environment changed')
  if observer.read_config(env['WINDOW_QA_HELPER_CONFIG'])!=config:raise RuntimeError('Terminal helper configuration changed')
  for witness in expected.values():
   for key in ('source','actual'):
    if observer.material_witness(witness[key]['path'])!=witness[key]:raise RuntimeError('Terminal QML source/path/mode changed')
  remaining(deadline)
 def invoke(method):
  guard();result=lifecycle.invoke('terminal-'+method,[str(lifecycle.launcher),'hoskinson.windows',method,nonce],seconds=min(4,remaining(deadline)))
  record['controlCalls'].append(dict(method=method,utcNs=time.time_ns(),returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
  if result.returncode!=0 or result.stderr:raise RuntimeError('Actual terminal control IPC failed')
  answer=json.loads(result.stdout,object_pairs_hook=unique);guard();return answer
 last=None
 try:
  answer=invoke('qaTerminalQuiesce')
  while True:
   remaining(deadline);processes_closed=validate(answer,nonce,outputs,last)
   with locked_until(config['log'],deadline)as stream:
    rows=observer.rows(stream);record['lastRawHelperRows']=rows;remaining(deadline)
    # Strict helper normal0; terminal maintenance exceptions do not apply.
    helper_closed=evaluation_setup.terminal_closure(rows)
    remaining(deadline);pending=evaluation_setup.pending_helper_processes(config,deadline)
   record['samples'].append(dict(utcNs=time.time_ns(),monotonic=time.monotonic(),answer=answer,actualProcessReceiptsClosed=processes_closed,rawHelperRows=rows,helperNormalClosed=helper_closed,unloggedExactHelpers=pending))
   if len(record['samples'])>300 or len(json.dumps(record))>33554432:raise RuntimeError('Bounded terminal evidence limit')
   if processes_closed and helper_closed and not pending:
    guard();record['accepted']=True;record['acceptedUtcNs']=time.time_ns();record['sourceWitnesses']=expected;return record
   last=answer;time.sleep(min(.03,remaining(deadline)));answer=invoke('qaTerminalRead')
 except BaseException as error:
  record['error']=repr(error);record['accepted']=False;raise
 finally:
  record['finishedUtcNs']=time.time_ns();path=Path(output)/'qs-terminal-drain.json'
  fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
  with os.fdopen(fd,'w')as stream:json.dump(record,stream,indent=2);stream.write('\n')
