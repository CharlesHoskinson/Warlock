#!/usr/bin/env python3
"""Independent read-only held terminal replay. No producer imports or native IPC."""
from pathlib import Path
import argparse,hashlib,json,math,os,re,stat,time,traceback
B=Path(__file__).resolve().parent

def witness(row):return (row.st_dev,row.st_ino,row.st_uid,row.st_mode,row.st_size,row.st_mtime_ns,row.st_ctime_ns)
def read(path,limit=134217728):
 path=Path(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC);data=bytearray()
 try:
  before=os.fstat(fd)
  if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or before.st_size>limit:raise ValueError('Unsafe bounded regular artifact: '+str(path))
  while chunk:=os.read(fd,1048576):
   data.extend(chunk)
   if len(data)>limit:raise ValueError('Artifact limit exceeded')
  if len(data)!=before.st_size or witness(before)!=witness(os.fstat(fd)) or witness(before)!=witness(path.lstat()):raise ValueError('Full EOF artifact changed during replay')
  return bytes(data)
 finally:os.close(fd)
def js(path):return json.loads(read(path))
def digest(path):
 path=Path(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC);h=hashlib.sha256();size=0
 try:
  before=os.fstat(fd)
  if not stat.S_ISREG(before.st_mode) or before.st_size>2147483648:raise ValueError('Unsafe bounded source file')
  while chunk:=os.read(fd,1048576):size+=len(chunk);h.update(chunk)
  if size!=before.st_size or witness(before)!=witness(os.fstat(fd)) or witness(before)!=witness(path.lstat()):raise ValueError('Source changed during replay')
  return h.hexdigest(),stat.S_IMODE(before.st_mode)
 finally:os.close(fd)
def identity(row):
 if not isinstance(row,dict) or not re.fullmatch(r'0x[0-9a-f]{1,16}',str(row.get('address',''))) or not re.fullmatch(r'[0-9a-f]{1,16}',str(row.get('stableId',''))) or type(row.get('pid')) is not int or not 0<row['pid']<(1<<31):raise ValueError('Malformed exact native identity')
 return (row['address'],row['stableId'],row['pid'])
def eq(a,b):
 try:return identity(a)==identity(b)
 except ValueError:return False
def groups(native):
 return sorted((identity(g['head']),identity(g['current']),tuple(identity(w) for w in g['members']),g['locked'],g['denied']) for g in native['groups'])
def clear(native):return native['coreDragTarget'] is None and native['signalDownButtonIds']==[] and native['heldButtons'] is False and all(not native[k] for k in ('sessionLocked','exclusiveLayers','constrained','seatGrab','captured','dnd'))
def gone(row):
 if type(row.get('pid')) is not int or not str(row.get('start','')).isdigit():raise ValueError('Malformed captured process identity')
 try:
  info=Path('/proc',str(row['pid']),'stat').read_text().rsplit(')',1)[1].split();return info[19]!=str(row['start']) or ('pgid' in row and int(info[2])!=row['pgid'])
 except FileNotFoundError:return True

def input_replay(cleanup,kind):
 if cleanup.get('exitCode')!=0 or cleanup.get('normalEOF') is not True or cleanup.get('knownDownTransitionsReleased') is not True:return False
 expected=cleanup['identity'];down=set();last=-1
 for row in cleanup['trace']:
  if row['pid']!=expected['pid'] or str(row['start'])!=str(expected['start']) or row['sentNs']<=last:return False
  last=row['sentNs'];parts=row['command'].split()
  if parts[0] in ('button','key'):
   if parts[0]!=('button' if kind=='pointer' else 'key') or len(parts)!=3:return False
   code,state=map(int,parts[1:])
   if state not in (0,1) or (code in down)==bool(state):return False
   if state:down.add(code)
   else:down.remove(code)
  elif parts[0]=='absolute':
   if kind!='pointer' or len(parts)!=5:return False
   x,y,w,h=map(float,parts[1:])
   if not all(math.isfinite(v) for v in (x,y,w,h)) or not(0<=x<w<=400000 and 0<=y<h<=400000):return False
  elif parts!=['sync']:return False
 return not down and bool(cleanup['trace']) and gone(expected)

def one(rows,key,value):
 hits=[row for row in rows if row.get(key)==value]
 if len(hits)!=1:raise ValueError('One exact '+value+' observation required')
 return hits[0]
def inside(point,box):return len(point)==2 and len(box)==4 and all(math.isfinite(v) for v in [*point,*box]) and box[2]>0 and box[3]>0 and box[0]<=point[0]<box[0]+box[2] and box[1]<=point[1]<box[1]+box[3]
def case_replay(case,expected,toolkit):
 trace=case['trace'];gates=case['gates'];initial=one(trace,'label','case baseline')['native'];press=one(trace,'label','actual press');target=press['target'];focus=one(trace,'label','separate WM focus intervention')['native'];peer=focus['nativeFocus']
 if case['case']!=expected['name'] or case['result']!='pass' or not clear(initial) or not gates or any(row.get('passed') is not True for row in gates):return False
 button=expected['button'];kind=expected['kind']
 if press['native']['signalDownButtonIds']!=[button] or not eq(one(trace,'label','actual native press allocation')['native']['hitOwner'],target):return False
 if kind=='pending':
  if press['native']['coreDragTarget'] is not None or focus['coreDragTarget'] is not None:return False
 else:
  captured=one(gates,'name','Held real gesture captured exact lifetime mode type and raw signal')['native']
  for state in (captured,focus):
   if not eq(state['coreDragTarget'],target) or state['coreDragMode']!=expected['nativeMode'] or state['coreDragTargetType']!=0 or state['signalDownButtonIds']!=[button]:return False
  geometry=one(gates,'name','Actual held gesture changed source geometry only')
  if geometry['press']==geometry['current']:return False
 if expected['name']=='genuine-group-release-positive':
  release=one(gates,'name','Only genuine actual release inserts exact source into peer group')['native']
  if not clear(release) or not any(len(g['members'])==2 and eq(g['head'],peer) and {identity(w) for w in g['members']}=={identity(target),identity(peer)} for g in release['groups']):return False
 else:
  retirement=one(gates,'name','Actual nonrelease retirement preserves groups raw hold and independent focus');before=retirement['before'];after=retirement['after']
  if after['coreDragTarget'] is not None or groups(before)!=groups(after) or after['signalDownButtonIds']!=before['signalDownButtonIds'] or after['signalDownButtonIds']!=[button] or not eq(after['nativeFocus'],peer):return False
  if expected.get('end')=='unload-reload':
   middle=one(trace,'label','actual native state between unload/reload')['native']
   if middle['coreDragTarget'] is not None or middle['signalDownButtonIds']!=[button] or groups(middle)!=groups(before) or not eq(middle['nativeFocus'],peer):return False
  release=one(gates,'name','Genuine release creates no group insertion or public callback leak')
  if not clear(release['native']) or groups(release['native'])!=groups(before):return False
  for role,count in release['counts'].items():
   if release['public']['windows'][role]['clicks' if toolkit=='QtWidgets' else 'callbacks']!=count:return False
 for role in (('source',) if expected['name']=='genuine-group-release-positive' else ('source','peer')):
  callback=one(gates,'name','Actual public callback after release '+role)
  if type(callback['before']) is not int or callback['after']!=callback['before']+1 or not clear(callback['nativeBefore']) or not clear(callback['nativeAfter']) or not eq(callback['nativeBefore']['hitOwner'],callback['nativeBefore']['pointerOwner']):return False
  native=[row for row in callback['nativeBefore']['windows'] if eq(row,callback['nativeBefore']['pointerOwner'])]
  if len(native)!=1 or not inside(callback['point'],native[0]['surfaceBox']):return False
  if any(abs(a-b)>.5 for a,b in zip(callback['point'],callback['nativeBefore']['cursor'])):return False
 if expected['name']!='genuine-group-release-positive':
  peer_geometry=one(gates,'name','Independent peer geometry remains exact after complete case')
  if peer_geometry['expected']!=peer_geometry['actual']:return False
 return True

def frontend_replay(case,events,shell_pid):
 click=one(case['trace'],'label','genuine widget preview native click authority');target=click['preview']['address'];point=click['point'];native=click['nativeBefore'];layer=click['previewLayer'];owner=native['pointerLayerOwner']
 if layer['pid']!=shell_pid or layer['namespace']!='hoskinson-taskbar-popup' or layer['mapped'] is not True or not inside(point,layer['box']) or owner is None or owner['pid']!=shell_pid or owner['namespace']!=layer['namespace'] or not owner['mapped']:return False
 if any(abs(a-b)>.5 for a,b in zip(point,native['cursor'])):return False
 accepted=[row for row in events if row.get('result')=='accepted' and row['request']['operation']=='restore' and row['request']['address']==target]
 if len(accepted)!=1:return False
 row=accepted[0];answer=row['answer'];authority=row['authority']
 if authority['root']!='shell' or authority['requester']['pid']!=shell_pid or row['transport']['completeServerEOF'] is not True or answer.get('ok') is not True or answer.get('accepted') is not True or answer.get('completed') is not False or type(answer.get('receipt')) is not int or answer['receipt']<1:return False
 identity(row['request']);restore=one(case['gates'],'name','Genuine preview frontend restored complete family with deepest modal focus');minimized=one(case['gates'],'name','Real held minimize capture seed native presentation and cache retirement')
 return restore['frontendReceipt']==row and minimized['receipt'].get('accepted') is True and presentation_replay(minimized['packet'],'minimize') and presentation_replay(restore['retirement'],'restore') and {r['source']:r['sha256'] for pair in minimized['packet']['cachePairsAtCapture'] for r in pair['files']}=={r['source']:r['sha256'] for pair in restore['retirement']['cachePairsAtCapture'] for r in pair['files']}

def presentation_replay(packet,operation):
 retirement=packet['retirement'];rows=packet['retainedEpochSources'];events=packet['rendererEvents']
 if len(rows)!=3 or not all(retirement[k] is True for k in ('actorDirectoryGone','originalRetirementDelegatedOnce','productRegistryRemoved','rendererClosed')) or retirement['rendererExitCode']!=0 or retirement['observedControllerBindings']!=1:return False
 for row in rows:
  if row['captureCallbackDelegatedOnce'] is not True or row['sourceResultUnchanged'] is not True or digest(row['retainedPath'])[0]!=row['sha256'] or row['source']['digest']!=row['sha256']:return False
 records=[row for row in packet['history'] if row['operation']==operation and len(row['sources'])==3 and all(any(source==retained['source'] for retained in rows) for source in row['sources'])]
 valid=[]
 for record in records:
  if record['validated'] is not True or record['ready'] is not True or record['profile'].get('failure') or record['profile'].get('settlementFailure') or record['profile'].get('settlementReason')!='native handover complete':continue
  token=record['token'];sources=record['sources'];digests=[{k:row[k] for k in ('stableId','pid','digest')} for row in sources]
  if len(record['results'])!=3 or any(row['operation']!=operation or row['reason']!=('presented ready' if operation=='minimize' else 'presented endpoint') for row in record['results']):continue
  if not all(any(row.get('event')=='uploaded' and row.get('digest')==source['digest'] and row.get('pixels')==source['pixels'] for row in events) for source in sources):continue
  if not any(row.get('event')=='seeded' and row.get('token')==token and row.get('sourceDigests')==digests for row in events):continue
  if not any(row.get('event')==('ready' if operation=='minimize' else 'endpoint') and row.get('token')==token and row.get('servicePromoted') is True and row.get('sourceDigests')==digests for row in events):continue
  presentations=[row for row in events if row.get('event')=='presented' and row.get('accepted') is True and row.get('token')==token and [(str(m['stableId']),m['pid'],m['digest']) for m in row.get('members',[])]==[(str(m['stableId']),m['pid'],m['digest']) for m in sources]]
  if any(sum(row.get('event')=='swap' and row.get('success') is True and all(row.get(k)==presentation.get(k) for k in ('token','sequence','output','generation','members')) for row in events)==1 for presentation in presentations):valid.append(record)
 if len(valid)!=1:return False
 pairs=packet['cachePairsAtCapture']
 if len(pairs)!=3:return False
 for pair in pairs:
  if len(pair['files'])!=2 or {Path(row['source']).suffix for row in pair['files']}!={'.png','.json'}:return False
  if any(digest(row['retainedPath'])[0]!=row['sha256'] for row in pair['files']):return False
 return True

def qs_replay(variant,stage,journal):
 shell=one(variant['processes'],'role','taskbar-shell');expected=shell['identity'];cleanup=variant['cleanup']['shell'];ready=variant['exactQSReadiness'];records=journal['records']
 if cleanup.get('normalQuit') is not True or cleanup.get('naturallyExitedBeforeClose') or cleanup.get('exitCode')!=0 or cleanup.get('exactOriginalGone') is not True or ready.get('exactReady') is not True or ready['identity']!=expected or journal['identity']!=expected or journal.get('ready') is not True or journal.get('killSent') is not True or cleanup['records']!=records or ready['records']!=records:return False
 phase='startup';last=-1;startup_ok=0;selected=None;killed=0;ids=set()
 for record in records:
  if record['qsIdentity']!=expected or record.get('error') or record['startedNs']<=last or record['completedNs']<record['startedNs'] or not gone(record['processIdentity']) or record.get('originalProbeGone') is not True:return False
  last=record['completedNs'];key=(record['processIdentity']['pid'],record['processIdentity']['start'])
  if key in ids:return False
  ids.add(key);role=record['role']
  if role=='startup-ping':
   if phase!='startup' or record['command']!=[str(stage/'payload/omarchy/bin/omarchy-shell'),'shell','ping']:return False
   if record['returncode']==0 and record['stdout']=='ok\n' and record['stderr']=='':startup_ok+=1;phase='selection'
   elif record['returncode']!=1 or record['stdout']!='' or record['stderr'] not in ('omarchy-shell is not running\n','omarchy-shell is not ready\n'):return False
  elif role=='instance-selection':
   if phase!='selection' or record['command']!=['/usr/bin/qs','--no-color','list','-a','-j'] or record['returncode']!=0 or record['stderr']!='':return False
   if record['stdout']=='No running instances.\n':continue
   rows=json.loads(record['stdout'])
   if not isinstance(rows,list) or not rows or any(set(row)!={'id','pid','shell_id','config_path','launch_time'} or type(row['pid']) is not int for row in rows):return False
   selected=one(rows,'pid',expected['pid'])
   if selected['config_path']!=str(stage/'payload/omarchy/shell/shell.qml') or selected['shell_id']!=hashlib.md5(selected['config_path'].encode()).hexdigest() or selected!=cleanup['selectedInstance']:return False
  elif role=='normal-kill':
   if phase!='selection' or selected is None or record['command']!=['/usr/bin/qs','--no-color','kill','--pid',str(expected['pid'])] or record['returncode']!=0 or record['stderr']!='' or record['stdout']!='Killed '+selected['id']+'\n':return False
   killed+=1;phase='stopped'
  else:return False
 return startup_ok==1 and killed==1 and phase=='stopped' and gone(expected)

class Auditor:
 def __init__(self):self.checks={};self.errors={};self.inventory=[]
 def check(self,name,fn):
  try:self.checks[name]=fn() is True
  except BaseException:self.checks[name]=False;self.errors[name]=traceback.format_exc()
 def audit(self,stage,attempt):
  frozen=js(stage/'frozen-inputs.json');matrix=js(stage/'matrix.json');report=js(attempt/'report.json');manifest_sha=digest(stage/'frozen-inputs.json')[0]
  self.check('terminalReportRetainsActualFailure',lambda:report['result'] in ('pass','fail'))
  self.check('completeFrozenBytesModesLinks',lambda:all(digest(path)==(sha,frozen['inputModes'][path]) for path,sha in frozen['inputs'].items()) and all(Path(path).is_symlink() and os.readlink(path)==target for path,target in frozen['symlinks'].items()))
  self.check('exactSourceManifest',lambda:report['sourceManifestSHA256']==manifest_sha)
  self.check('all18MainPreservation',lambda:len(report['mainPreservation'])==18 and all(value is True for value in report['mainPreservation'].values()))
  self.check('mainWritesAbsent',lambda:report['mainWrites'] is False and report['mainRestorationWrites'] is False)
  expected={row['name']:row for row in matrix['variants']};actual=report['variants'];names=[row['variant'] for row in actual]
  self.check('allFourExactVariants',lambda:len(names)==4 and set(names)==set(expected) and len(names)==len(set(names)))
  for variant in actual:
   name=variant['variant'];folder=attempt/name;cases=variant['cases'];wanted=matrix['casesPerVariant'];toolkit=expected[name]['toolkit'];prefix=name+':'
   self.check(prefix+'all13ExactCases',lambda:len(cases)==13 and [row['case'] for row in cases]==[row['name'] for row in wanted])
   for index,case in enumerate(cases):
    self.check(prefix+case.get('case','unidentified')+':nativeReplay',lambda case=case,index=index:case_replay(case,wanted[index],toolkit))
    self.check(prefix+case.get('case','unidentified')+':normalPublicQuit',lambda case=case:case['cleanup']['normalPublicQuit'] is True and case['cleanup']['fixtureExitCode']==0 and case['cleanup']['exactOriginalProcessGone'] is True and any(row['command']=='quit' and row['ack'] is True and row['featureOracle'] is False for row in case['cleanup']['publicCommandAcknowledgements']))
   for kind in ('pointer','keyboard'):self.check(prefix+kind+'LegalBalancedActualTransitionsNormalEOF',lambda kind=kind:input_replay(variant['cleanup'][kind],kind))
   self.check(prefix+'exactQSReadinessAndExplicitNormalQuit',lambda:qs_replay(variant,stage,js(folder/'qs-lifecycle.json')))
   self.check(prefix+'normalQSAndService',lambda:all(variant['cleanup'][kind]['exitCode']==0 and variant['cleanup'][kind]['exactOriginalGone'] is True for kind in ('shell','service') if (kind=='shell' or any(row['role']=='held-service' for row in variant['processes']))) and not any(row.get('forcedTermination') or row.get('forcedKill') or row.get('error') for row in variant['cleanup'].values()))
   self.check(prefix+'nativeUnloadNormalOrdered',lambda:variant['normalNativeUnload'] is True and variant['actualNativeUnloadReply'].strip()=='ok' and variant['actualProbeUnloadReply'].strip()=='ok' and all(variant['nativeUnloadOrdering'][key] is True for key in ('genuineInputsReleasedNormally','normalToolkitLifetimesGone','normalShellServiceLifetimesGone','allExactHelperProcessesGone','clientListEmpty')))
   self.check(prefix+'hostRuntimeCleanup',lambda:self.host_cleanup(variant))
   self.check(prefix+'rawHelpersNormalExact',lambda:self.helpers(folder,variant))
   self.check(prefix+'allRecordedOriginalIdentitiesGone',lambda:self.processes_gone(variant))
   mins=[row for row in cases if row['case'].endswith('minimize-preview')]
   self.check(prefix+'bothGenuineShellPreviewReceipts',lambda:len(mins)==2 and self.previews(folder,variant,mins))
   self.inventory.append(dict(variant=name,reachedCases=len(cases),retainedResult=variant['result'],errors={key:variant[key] for key in ('error','helperAcceptanceError','serviceAcceptanceError') if key in variant}))
  full=report['result']=='pass' and len(actual)==4 and all(self.checks.values())
  return dict(result='pass' if full else 'fail',checks=self.checks,errors=self.errors,inventory=self.inventory,sourceManifestSHA256=manifest_sha,sourceCount=len(frozen['inputs']),modeCount=len(frozen['inputModes']),linkCount=len(frozen['symlinks']),actualReachedCases=sum(len(row['cases']) for row in actual),expectedCases=52,producerResult=report['result'],nativeCommands=False,mainWrites=False,fullWindowsParityAccepted=False,fullHeld52ReplayAccepted=full,replayLimitations=['Historical geometry/pin and native IPC command timing are accepted only where actual samples are retained; gate booleans alone do not supply missing observations.'],auditorSourceSHA256=digest(B/'audit.py')[0])
 def processes_gone(self,variant):
  rows=[]
  def visit(value):
   if isinstance(value,dict):
    if type(value.get('pid')) is int and str(value.get('start','')).isdigit():rows.append(value)
    for child in value.values():visit(child)
   elif isinstance(value,list):
    for child in value:visit(child)
  visit(variant);return bool(rows) and all(gone(row) for row in rows)
 def host_cleanup(self,variant):
  host=variant['hostEvidence'];runtime=host['runtime']
  if not re.fullmatch(r'/run/user/'+str(os.getuid())+r'/wqa/[0-9a-f]{4}',runtime):return False
  return host['runtimeGone'] is True and not Path(runtime).exists() and not host.get('remainingDescendants') and not host.get('unexpectedInnerDescendants') and not host.get('cleanupErrors')
 def helpers(self,folder,variant):
  archive=js(folder/'terminal-helpers/archive.json');cfg_raw=read(folder/'terminal-helpers/helper-config.json');log_raw=read(folder/'terminal-helpers/helper-events.jsonl');config=json.loads(cfg_raw);events=[json.loads(line) for line in log_raw.splitlines() if line.strip()]
  if hashlib.sha256(cfg_raw).hexdigest()!=archive['configSHA256'] or hashlib.sha256(log_raw).hexdigest()!=archive['logSHA256'] or archive['completeEOF'] is not True or events!=archive['events']:return False
  starts=[row for row in events if row['event']=='started'];ends=[row for row in events if row['event']=='terminal']
  if len(events)!=len(starts)+len(ends) or len(starts)!=len(ends):return False
  keys=[row['operation'] for row in starts]
  if len(keys)!=len(set(keys)):return False
  compositor=[row for row in starts if row.get('class','compositor')=='compositor'];queries=[row for row in starts if row.get('class')=='query']
  if set(row['operation'] for row in compositor)!=set(config['allowed']):return False
  if sum(row.get('queryRoot')=='harness' for row in queries)!=1 or not any(row.get('queryRoot')=='qs' for row in queries):return False
  if any(row.get('queryRoot') not in ('qs','harness','service') for row in queries):return False
  for start in starts:
   end=one(ends,'operation',start['operation'])
   if end['exitCode']!=0 or any(end.get(key)!=start.get(key) for key in ('wrapper','delegate','class','queryRoot','helper','serviceOperation')) or not gone(start['wrapper']) or not gone(start['delegate']) or start['ipc']['completeServerEOF'] is not True:return False
  service=[row for row in queries if row.get('queryRoot')=='service'];members=config['serviceMembers'];expected={('service-motionTarget:'+row['address']+':'+row['stableId']+':'+str(row['pid'])):config['serviceTargetLimitPerMember'] for row in members};expected['service-motionRefresh']=config['serviceRefreshLimit']
  return len(service)==sum(expected.values()) and all(sum(row['serviceOperation']==key for row in service)==count for key,count in expected.items())
 def previews(self,folder,variant,cases):
  journal=js(folder/'frontend-events.json');shell=one(variant['processes'],'role','taskbar-shell')['identity']['pid']
  return all(frontend_replay(case,journal['events'],shell) for case in cases)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',type=Path,required=True);p.add_argument('--attempt',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();stage=a.stage.resolve();attempt=a.attempt.resolve();output=a.output.absolute()
 if attempt.parent!=stage or not attempt.name.startswith('attempt-') or output.parent!=attempt or output.is_symlink():raise ValueError('Exact owned attempt and additive output required')
 fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  try:result=Auditor().audit(stage,attempt)
  except BaseException:result=dict(result='fail',auditorError=traceback.format_exc(),nativeCommands=False,mainWrites=False,fullHeld52ReplayAccepted=False)
  with os.fdopen(fd,'w',closefd=False) as stream:json.dump(result,stream,indent=2);stream.write('\n');stream.flush();os.fsync(fd)
 finally:os.close(fd)
 print(json.dumps(dict(result=result['result'],artifact=str(output),checks=len(result.get('checks',{})),passed=sum(result.get('checks',{}).values()),nativeCommands=False)));return int(result['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
