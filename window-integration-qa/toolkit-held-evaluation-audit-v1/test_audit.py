"""Synthetic retained-record faults only; no producer import/native execution."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import audit as a
BASE=Path(__file__).resolve().parent;PREV=BASE.parent/'toolkit-held-matrix-v7'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def material(path):
 row=path.stat();return dict(path=str(path),sha256=sha(path),identity=[row.st_dev,row.st_ino,row.st_uid,row.st_mode,row.st_size,row.st_mtime_ns,row.st_ctime_ns],completeEOF=True)
def put(path,row):path.parent.mkdir(mode=0o700,parents=True,exist_ok=True);path.write_text(json.dumps(row));path.chmod(0o600)
def fixture(root):
 stage=root/'stage';stage.mkdir();folder=root/'attempt'/'qt-wayland';folder.mkdir(parents=True)
 inputs={};modes={}
 def include(path):inputs[str(path)]=sha(path);modes[str(path)]=path.stat().st_mode&0o7777
 for name in ('helper_observer.py','helper_setup.py','evaluation_setup.py','held_route.py','run_native.py'):
  shutil.copyfile(PREV/name,stage/name);include(stage/name)
 shell=stage/'payload/omarchy/bin/omarchy-shell';shell.parent.mkdir(parents=True);shutil.copyfile(PREV/'payload/omarchy/bin/omarchy-shell',shell);include(shell)
 native=stage/'candidate.so';native.write_bytes(b'synthetic artifact never loaded');native.chmod(0o600);include(native)
 probe=stage/'probe.so';probe.write_bytes(b'synthetic probe never loaded');probe.chmod(0o600);include(probe)
 backend=BASE.parent/'snap-close-identity-v1/hypr-snap-groups';include(backend)
 executable=Path('/proc/self/exe').resolve();include(executable)
 frozen=dict(inputs=inputs,inputModes=modes,symlinks={})
 guard=a.source_guards(stage,frozen);runtime=root/'runtime';runtime.mkdir()
 configuration=runtime/'hyprland.lua';configuration.write_text('synthetic owned context\n'+guard['initialFullSnapPrologue']);configuration.chmod(0o600)
 archive_path=folder/'host/runtime-archive/hyprland.lua';archive_path.parent.mkdir(parents=True);shutil.copyfile(configuration,archive_path);archive_path.chmod(0o600)
 compositor=dict(pid=30000000,start='123');authorizer=dict(identity=dict(pid=30000001,start='124',pgid=30000001,parent=1),argv=['/usr/bin/python3',str(stage/'run_native.py'),'--attempt','synthetic'],source=str(stage/'run_native.py'),sourceSHA256=sha(stage/'run_native.py'),executable=str(executable),executableSHA256=sha(executable))
 home=runtime/'taskbar-home';helpers={}
 for kind,name,path in [('snap','hypr-snap-groups',backend),('shell','omarchy-shell',shell)]:helpers[kind]=dict(wrapper=str(home/'.local/bin'/name),wrapperSHA256=sha(stage/'helper_observer.py'),actual=str(home/'.local/bin'/(name+'.actual')),actualSHA256=sha(path))
 config=dict(compositor=compositor,instance='synthetic-record-only',socketIdentity=[7,8,os.getuid()],versionSHA256='e'*64,evaluationConfiguration=material(configuration),evaluationArtifacts=dict(native=material(native),probe=material(probe)),evaluationInitialCommand=['repl','synthetic full paired source'],evaluationTickets=[],activeEvaluation=None,queryRoots=dict(harness=authorizer),helpers=helpers,allowed=[])
 proof=dict(request='j/version',completeServerEOF=True,peer=dict(pid=compositor['pid'],uid=os.getuid(),gid=os.getgid()),socketIdentity=config['socketIdentity'],replySHA256=config['versionSHA256'])
 events=[];completed={};host_lines=[' [PluginSystem] Plugin hyprbars loaded.'];kinds=['initial','native-unload','native-load','reload','native-unload','probe-unload']
 for index,kind in enumerate(kinds,1):
  artifact=None if kind in ('initial','reload') else config['evaluationArtifacts']['probe' if kind=='probe-unload' else 'native'];nonce=hex(index)[2:]*32
  ticket=dict(serial=index,nonce=nonce,kind=kind,count=a.RULES[kind][0],relayOrdinal=a.RULES[kind][1],command=config['evaluationInitialCommand'] if kind=='initial' else ['reload'] if kind=='reload' else ['plugin','load' if kind=='native-load' else 'unload',artifact['path']],root=copy.deepcopy(authorizer),compositor=copy.deepcopy(compositor),instance=config['instance'],configuration=config['evaluationConfiguration'],artifact=artifact,armIPC=proof,armedNs=1000*index,terminalAuthority=index>len(kinds)-2)
  config['evaluationTickets'].append(ticket);config['allowed']+=a.keys(ticket);config['activeEvaluation']=nonce
  if kind=='native-load':host_lines.append(' [PluginSystem] Plugin hyprbars loaded.')
  if kind=='native-unload':host_lines.append(' [PluginSystem] Plugin hyprbars unloaded.')
  if kind=='probe-unload':host_lines.append(' [PluginSystem] Plugin toolkit_held_probe unloaded.')
  for offset,key in enumerate(a.keys(ticket),1):
   ordinal=key.rsplit(':',2)[1];base=key.rsplit(':',1)[1];pid=30010000+index*100+offset;helper='snap' if base=='hydrate' else 'shell'
   start=dict(event='started',operation=key,args=['hydrate'] if helper=='snap' else ['hoskinson.windows','fileDrag','false','1','2','0','3'],helper=helper,wrapper=dict(pid=pid,start=str(pid),pgid=compositor['pid'],parent=compositor['pid']),delegate=dict(pid=pid+30,start=str(pid+30),pgid=compositor['pid'],parent=pid),ancestry=[dict(compositor,pgid=compositor['pid'],parent=1)],ipc=proof,actual=helpers[helper]['actual'],actualSHA256=helpers[helper]['actualSHA256'],evaluationEnvironment=dict(zip(a.ENV,[nonce,kind,str(ticket['count']),ordinal])),timeNs=ticket['armedNs']+offset*10,queryRoot=None)
   start['class']='compositor';end={k:start[k] for k in ('operation','helper','wrapper','delegate','class','queryRoot')};end.update(event='terminal',exitCode=0,timeNs=start['timeNs']+1);events.extend([start,end])
   if helper=='snap':host_lines += ['[executor] Executing '+helpers['snap']['wrapper']+' hydrate','[executor] Process created with pid '+str(pid)]
  completed[index]=dict(ticket=ticket,completionIPC=proof,actualOrdinal=ticket['count'],expectedOperations=a.keys(ticket),events=copy.deepcopy(events),allExactProcessesGone=True,unloggedExactHelperProcesses=[],allExpectedNormal=True,fullEOF=True,terminalAuthority=ticket['terminalAuthority'])
 variant=dict(variant='qt-wayland',result='pass',cases=[dict(case='move-unload-reload',result='pass')],evaluationTickets=config['evaluationTickets'],completedEvaluations=list(range(1,len(kinds)+1)),normalNativeUnload=True,actualProbeUnloadReply='ok',hostEvidence=dict(compositorPID=compositor['pid'],compositorStart=compositor['start'],compositorConfig=str(configuration),compositorConfigSHA256=sha(configuration)),reloadConfigurationWitness=dict(sha256=sha(configuration),device=configuration.stat().st_dev,inode=configuration.stat().st_ino),nativeUnloadOrdering={k:True for k in ('genuineInputsReleasedNormally','normalToolkitLifetimesGone','normalShellServiceLifetimesGone','allExactHelperProcessesGone','clientListEmpty')})
 matrix=dict(candidate=str(native),probe=str(probe),pairedCloseHelper=str(backend));host=folder/'host/hyprland.log';host.write_text('\n'.join(host_lines));host.chmod(0o600)
 return dict(stage=stage,folder=folder,variant=variant,matrix=matrix,frozen=frozen,guard=guard,config=config,events=events,completed=completed)

def archive(data):
 folder=data['folder'];cfg=json.dumps(data['config']).encode();log=b'\n'.join(json.dumps(row).encode() for row in data['events'])+b'\n'
 target=folder/'terminal-helpers';target.mkdir(exist_ok=True);(target/'helper-config.json').write_bytes(cfg);(target/'helper-events.jsonl').write_bytes(log)
 for path in target.iterdir():path.chmod(0o600)
 put(target/'archive.json',dict(configSHA256=hashlib.sha256(cfg).hexdigest(),logSHA256=hashlib.sha256(log).hexdigest(),completeEOF=True,parseErrors=[],events=data['events']))
 for index,row in data['completed'].items():put(folder/('evaluation-'+str(index)+'.json'),row)
 put(folder/'final-completed-helpers.json',dict(config=data['config'],events=data['events'],allNormal=True,allExactProcessesGone=True))

def replay(data):
 archive(data)
 with patch.object(a.reader,'gone',return_value=True):return a.replay_variant(*(data[k] for k in ('stage','folder','variant','matrix','frozen','guard')))

class ReplayFaults(unittest.TestCase):
 def test_normal_synthetic_records_replay_without_claiming_whole52(self):
  with tempfile.TemporaryDirectory() as directory:
   row=replay(fixture(Path(directory)));self.assertEqual(row['normalCallbacks'],10);self.assertEqual([t['kind'] for t in row['tickets']],['initial','native-unload','native-load','reload','native-unload','probe-unload']);self.assertFalse(row['separatePostGateSnapshotRetained'])
 def fault(self,mutate,pattern):
  with tempfile.TemporaryDirectory() as directory:
   data=fixture(Path(directory));mutate(data)
   # Keep the tampered archival samples mutually consistent so semantic guards,
   # rather than an incidental prefix mismatch, must reject these faults.
   for row in data['completed'].values():row['events']=copy.deepcopy(data['events'][:len(row['events'])])
   with self.assertRaisesRegex(ValueError,pattern):replay(data)
 def test_changed_nonce_or_child_ordinal_or_kind(self):
  for field,value in [(a.ENV[0],'d'*32),(a.ENV[3],'2'),(a.ENV[1],'reload')]:
   self.fault(lambda d:d['events'][0]['evaluationEnvironment'].update({field:value}),'Actual child')
 def test_duplicate_or_extra_or_refused_or_missing_terminal(self):
  self.fault(lambda d:d['events'].append(copy.deepcopy(d['events'][0])),'Missing/duplicate')
  self.fault(lambda d:d['events'].append(dict(event='refused',exitCode=125,delegateExecuted=False)),'Extra/refused')
  self.fault(lambda d:d['events'].pop(),'Missing/duplicate')
 def test_ipc_full_eof_peer_or_socket_mismatch(self):
  for field,value in [('completeServerEOF',False),('socketIdentity',[7,9,os.getuid()]),('replySHA256','f'*64)]:self.fault(lambda d:d['config']['evaluationTickets'][0]['armIPC'].update({field:value}),'peer/socket/version/fullEOF')
 def test_precommand_armed_time_or_command_changes(self):
  self.fault(lambda d:d['config']['evaluationTickets'][1].update(armedNs=1),'Ticket root/lifetime/serial/source/config chronology')
  self.fault(lambda d:d['config']['evaluationTickets'][1].update(command=['reload']),'artifact command')
 def test_root_source_argv_or_exact_compositor_changed(self):
  self.fault(lambda d:d['config']['queryRoots']['harness'].update(sourceSHA256='0'*64),'frozen source')
  self.fault(lambda d:d['config']['queryRoots']['harness'].update(argv=['/usr/bin/python3','other']),'authorizing harness')
  self.fault(lambda d:d['config']['compositor'].update(start='999'),'compositor PID/start')
 def test_artifact_byte_inode_and_config_archive_changes(self):
  self.fault(lambda d:Path(d['matrix']['candidate']).write_bytes(b'changed owned data'),'frozen source')
  self.fault(lambda d:(d['folder']/'host/runtime-archive/hyprland.lua').write_text('changed'),'startup configuration')
 def test_native_ancestry_or_terminal_start_identity_changes(self):
  self.fault(lambda d:d['events'][0]['wrapper'].update(parent=1),'ancestry')
  self.fault(lambda d:d['events'][1].update(wrapper=dict(pid=5,start='5')),'normal helper terminal')
 def test_completion_extra_ordinal_or_unlogged_helper_refuses(self):
  self.fault(lambda d:d['completed'][1].update(actualOrdinal=2),'actual evaluation completion')
  self.fault(lambda d:d['completed'][1].update(unloggedExactHelperProcesses=[{'pid':1}]),'actual evaluation completion')
 def test_late_extra_guard_fault_or_new_native_executor_refuses(self):
  self.fault(lambda d:(d['folder']/'host/hyprland.log').write_text((d['folder']/'host/hyprland.log').read_text()+'\nUnexpected extra private Lua evaluation\n'),'prologue fault')
  self.fault(lambda d:(d['folder']/'host/hyprland.log').write_text((d['folder']/'host/hyprland.log').read_text()+'\n[executor] Executing '+d['config']['helpers']['snap']['wrapper']+' hydrate\n[executor] Process created with pid 39999999\n'),'executor fork')
 def test_terminal_cleanup_cannot_bypass_normal_input_client_root_ordering(self):
  self.fault(lambda d:d['variant']['nativeUnloadOrdering'].update(genuineInputsReleasedNormally=False),'owned lifetime ordering')
 def test_duplicate_json_and_nonfinite_values_refuse(self):
  with self.assertRaisesRegex(ValueError,'Duplicate'):a.parse('{"same":1,"same":2}')
  with self.assertRaisesRegex(ValueError,'Nonfinite'):a.parse('{"value":NaN}')
if __name__=='__main__':unittest.main()
