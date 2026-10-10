"""UI-006 durable workspace navigation model."""
import copy,hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
out=root/'qa/runs'/('workspace-navigation-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'protectedScope':scope,'commands':[],'inputs':{str(p):sha(p) for p in [root/'qa/empty-workspace-navigation.qnt',root/'qa/empty-workspace-navigation_test.qnt']},'scope':'Host/broker durable admission before native dispatch, owner/context refusal, lost ACK, restart exact read without replay, Unknown dismissal. Abstract one navigation and window exclusion; disk atomicity, wire validation, native API/pixels/AT/deadlines require separate evidence.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 for name,path,args in [('typecheck','empty-workspace-navigation.qnt',['typecheck']),('tests-typecheck','empty-workspace-navigation_test.qnt',['typecheck']),('compat-tests-typecheck','workspace-navigation_test.qnt',['typecheck']),('named','empty-workspace-navigation_test.qnt',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=79571']),('witness-safety','empty-workspace-navigation.qnt',['run','--backend=typescript','--invariants=safety','--witnesses','commitWitness','refusalWitness','recoveredWitness','unknownWitness','--max-samples=1000','--max-steps=30','--seed=79572'])]:
  command=['quint',args[0],str(root/'qa'/path),*args[1:]];p=subprocess.run(command,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'command':command,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr
  if name=='witness-safety':
   counts={n:int(c) for n,c in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',p.stdout)};assert len(counts)==4 and all(counts.values());report['witnesses']=counts
 if sys.argv[1:]!=['--model-only']:
  assert not sys.argv[1:]
  import os,tempfile,shlex
  sys.path.insert(0,str(root/'adapter'))
  from workspace_navigation import Navigation,NAME,record,intent,encoded
  from recovery_store import RecoveryStore
  from endpoint import Refused
  fixture=out/'host-workspace-fixture.c';fixture.write_text('''#include <glib.h>
#include <json-glib/json-glib.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include "surface.h"
#include "host-journal.h"
int main(int argc,char **argv) {
 if(argc!=4)return 2;
 JsonParser *bound=json_parser_new(),*requests=json_parser_new();
 if(!json_parser_load_from_data(bound,argv[2],-1,NULL) || !json_parser_load_from_data(requests,argv[3],-1,NULL))return 2;
 if(!admission_open(argv[1]) || !admission_bind(json_parser_get_root(bound)))return 2;
 gboolean ok=admission_batch(json_node_get_array(json_parser_get_root(requests)),json_parser_get_root(bound));
 admission_close();g_object_unref(bound);g_object_unref(requests);return ok?0:1;
}
''')
  flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0'],text=True))
  command=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-I'+str(root/'native'),str(fixture),'-o',str(out/'host-workspace-fixture'),*flags,'-lm'];p=subprocess.run(command,capture_output=True,text=True);(out/'host-compile.stdout').write_text(p.stdout);(out/'host-compile.stderr').write_text(p.stderr);report['commands'].append({'name':'real-host-journal-compile','command':command,'exitCode':p.returncode});assert p.returncode==0,p.stderr
  checks={}
  bound={'lifetime':'1','session':'1','frontend':'1'}
  selected={'request':'1','generation':'1','source':{'identity':'1','generation':'1','monitor':'0','outputOwnershipGeneration':'1'},'destination':{'identity':'3','generation':'3','monitor':'0','outputOwnershipGeneration':'1'},'context':{'lifetime':'1','epoch':'1','output':'1','revision':'1'}}
  def request(value):return {'protocolVersion':3,'kind':'workspace-navigation','workspaceProtocol':1,'binding':bound,'intent':value}
  class Client:
   def __init__(self,store):self.bound=bound;self.store=store;self.submissions=0;self.reads=0;self.retained=None;self.lose_ack=False;self.forge=False
   def request(self,value):
    if value['kind']=='workspace-navigation':
     assert self.store._load()['status']=='Unknown';self.submissions+=1
     self.retained={'schema':1,'binding':bound,'intent':copy.deepcopy(value['intent']),'status':'Committed','reason':'applied'}
     if self.lose_ack:raise OSError('fixture lost native ACK')
     result={'protocolVersion':3,'kind':'workspace-navigation-outcome','workspaceProtocol':1,**{k:self.retained[k] for k in ['binding','intent','status','reason']}}
     if self.forge:result['intent']=dict(result['intent'],request='999')
     return result
    assert value['kind']=='workspace-navigation-state-request';self.reads+=1
    retained=self.retained or {'schema':1,**copy.deepcopy(value['record']),'status':'Unknown','reason':'native-record-unavailable'}
    return {'protocolVersion':3,'kind':'workspace-navigation-state','workspaceProtocol':1,'binding':bound,'requestId':value['requestId'],'record':retained}
  with tempfile.TemporaryDirectory(prefix='workspace-navigation-',dir=out) as directory:
   runtime=pathlib.Path(directory).resolve();os.chmod(runtime,0o700);config=runtime/'authority.json';config.write_text(json.dumps({'runtime':str(runtime),'instance':'fixture'}));os.chmod(config,0o600)
   def host(requests):
    p=subprocess.run([str(out/'host-workspace-fixture'),str(config),json.dumps(bound),json.dumps(requests)],capture_output=True,text=True)
    assert p.returncode in [0,1],p.stderr;return p.returncode==0
   with RecoveryStore(runtime,'fixture','1') as recovery:
    nav=Navigation(recovery);client=Client(nav)
    assert host([request(selected)]);assert nav._load()['status']=='Pending';checks['actualHostPersistsBeforeBroker']=True
    assert not host([request(selected)]);checks['duplicateHostAdmissionBlocked']=True
    window={'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':bound,'intent':{'request':'1','generation':'1','incarnation':'1','operation':'activate','context':selected['context']}}
    assert not host([window]);checks['hostBlocksWindowDuringNavigation']=True
    result=nav.handle(client,request(selected));assert result['status']=='Committed' and client.submissions==1 and nav._load()['status']=='Committed';checks['brokerUnknownBeforeNativeAndExactCommit']=True
    try:nav.handle(client,request(selected))
    except Refused:pass
    else:raise AssertionError('replay admitted')
    assert client.submissions==1;checks['duplicateBrokerNeverSubmits']=True
    assert not host([request(selected)]);checks['terminalCounterCannotBeReused']=True
    next_intent=dict(selected,request='2',generation='2');assert host([request(next_intent)]);client.lose_ack=True
    try:nav.handle(client,request(next_intent))
    except OSError:pass
    else:raise AssertionError('lost ACK missing')
    assert nav._load()['status']=='Unknown' and client.submissions==2;checks['lostAckDurableUnknown']=True
    restarted=Navigation(recovery);client.store=restarted;frame=restarted.recover(client);assert frame['record']['status']=='Committed' and client.submissions==2 and client.reads==1;checks['restartReadsRetainedExactOutcomeWithoutReplay']=True
    third=dict(selected,request='3',generation='3');assert host([request(third)]);client.retained=None
    frame=restarted.recover(client);assert frame['record']['status']=='Unknown' and client.submissions==2;checks['hostOnlyCrashNeverDispatches']=True
    assert not host([request(dict(selected,request='4',generation='4'))]);checks['unknownBlocksNewWorkspaceAdmission']=True
    assert not host([window]);checks['unknownBlocksNewWindowAdmission']=True
    assert not host([window,request(third)]);checks['mixedMutationBatchRejected']=True
    wrong=copy.deepcopy(third);wrong['destination']['generation']='0'
    assert not host([request(wrong)]);checks['hostRejectsInvalidWorkspaceOwner']=True
    damaged=recovery.path/NAME;original=damaged.read_bytes();damaged.unlink();damaged.symlink_to(config)
    assert not host([window]);checks['hostRejectsJournalSymlink']=True
    try:restarted.blocked()
    except (Refused,OSError):pass
    else:raise AssertionError('symlink accepted')
    checks['brokerRejectsJournalSymlink']=True;damaged.unlink();damaged.write_bytes(original);os.chmod(damaged,0o600)
  for name,mutate in {'zeroWorkspace':lambda i:i['destination'].update(identity='0'),'noncanonicalWorkspace':lambda i:i['destination'].update(identity='03'),'signedOverflow':lambda i:i['destination'].update(identity=str(1<<63)),'zeroOwner':lambda i:i['destination'].update(generation='0'),'negativeMonitor':lambda i:i['source'].update(monitor='-1'),'foreignEpoch':lambda i:i['context'].update(epoch='2'),'unknownField':lambda i:i.update(incarnation='1')}.items():
   bad=copy.deepcopy(selected);mutate(bad)
   try:intent(bad,bound)
   except Refused:checks[name]=True
   else:raise AssertionError(name)
  report['bridgeChecks']=checks
  for name in ['adapter/workspace_navigation.py','adapter/daemon.py','native/host-journal.h','native/surface.h']:report['inputs'][str(root/name)]=sha(root/name)

 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
