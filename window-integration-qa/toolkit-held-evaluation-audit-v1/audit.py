"""Independent additive evaluation replay. No producer imports, IPC or writes to stages."""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import traceback
BASE=Path(__file__).resolve().parent
READER=BASE.parent/'toolkit-held-terminal-audit-v2/audit.py'
spec=importlib.util.spec_from_file_location('independent_terminal_descriptor_reader',READER);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
RULES={'initial':(1,1),'reload':(1,1),'native-load':(2,2),'native-unload':(1,0),'probe-unload':(1,0)}
ENV=('WINDOW_QA_EVALUATION_NONCE','WINDOW_QA_EVALUATION_KIND','WINDOW_QA_EVALUATION_LIMIT','WINDOW_QA_EVALUATION_ORDINAL')

def unique(pairs):
 row={}
 for key,value in pairs:
  if key in row:raise ValueError('Duplicate artifact JSON key')
  row[key]=value
 return row

def parse(raw):return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite artifact JSON')))
def js(path):return parse(reader.read(path))
def need(value,message):
 if not value:raise ValueError(message)
def ident(row):
 need(type(row['pid']) is int and row['pid']>0 and re.fullmatch('[1-9][0-9]*',str(row['start'])),'Exact PID/start required')
 return row['pid'],str(row['start'])
def same(a,b):return ident(a)==ident(b)
def source(path,sha,frozen):
 path=str(path);need(frozen['inputs'].get(path)==sha and reader.digest(path)==(sha,frozen['inputModes'][path]),'Exact frozen source/mode differs: '+path)
def material(row,path,frozen):
 need(row['path']==str(path) and row['completeEOF'] is True,'Exact complete-EOF artifact path required')
 source(path,row['sha256'],frozen);info=Path(path).lstat()
 need(row['identity']==[info.st_dev,info.st_ino,info.st_uid,info.st_mode,info.st_size,info.st_mtime_ns,info.st_ctime_ns],'Exact artifact descriptor identity changed')
def ipc(row,config):
 need(row['completeServerEOF'] is True and row['request']=='j/version' and row['peer']['pid']==config['compositor']['pid'] and row['peer']['uid']==os.getuid() and row['socketIdentity']==config['socketIdentity'] and row['replySHA256']==config['versionSHA256'],'Selected exact peer/socket/version/fullEOF differs')
def keys(ticket):
 need(ticket['kind'] in RULES and type(ticket['serial']) is int and 1<=ticket['serial']<=100 and isinstance(ticket['nonce'],str) and re.fullmatch('[0-9a-f]{32}',ticket['nonce']),'Exact bounded nonce/serial/kind required')
 count,relay=RULES[ticket['kind']]
 need(type(ticket['count']) is int and type(ticket['relayOrdinal']) is int and (ticket['count'],ticket['relayOrdinal'])==(count,relay),'Source-backed callback obligations differ')
 prefix='evaluation:'+str(ticket['serial'])+':'+ticket['nonce']+':'
 return [prefix+str(n)+':hydrate' for n in range(1,count+1)]+([prefix+str(relay)+':inactive-fileDrag'] if relay else [])
def normal_events(events):
 starts=[row for row in events if row['event']=='started'];ends=[row for row in events if row['event']=='terminal']
 need(len(events)==len(starts)+len(ends),'Extra/refused/unknown helper event retained')
 need(len(starts)==len(ends) and len({r['operation'] for r in starts})==len(starts) and len({r['operation'] for r in ends})==len(ends),'Missing/duplicate helper start/terminal')
 for row in starts:
  end=reader.one(ends,'operation',row['operation'])
  need(end['exitCode']==0 and end['timeNs']>=row['timeNs'] and all(end.get(k)==row.get(k) for k in ('wrapper','delegate','class','queryRoot','helper','serviceOperation')),'Exact normal helper terminal differs')
  need(reader.gone(row['wrapper']) and reader.gone(row['delegate']),'Exact helper PID/start remains live')
 return starts,ends

def source_guards(stage,frozen):
 for name in ('helper_observer.py','evaluation_setup.py','helper_setup.py','held_route.py','run_native.py'):
  source(stage/name,frozen['inputs'][str(stage/name)],frozen)
 text=reader.read(stage/'helper_observer.py').decode();start=text.index('if child == 0:');end=text.index('os.execv(',start);gate=text[start:end]
 need("os.read(read_fd, 1) != b'1'" in gate and "evaluation_operation(read_config(config_path),os.environ,operation(args))!=key" in gate and "digest(config['actual'])!=config['actualSHA256']" in gate,'Frozen post-gate source/current selector guard absent')
 setup=ast.parse(reader.read(stage/'evaluation_setup.py').decode());prologue=ast.literal_eval(next(n.value for n in setup.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROLOGUE' for t in n.targets)))
 need(prologue.index('hl.env("WINDOW_QA_EVALUATION_ORDINAL"')<prologue.index('assert(evaluationOrdinal<='),'Actual prologue counter-before-bound guard differs')
 route=reader.read(stage/'held_route.py').decode();part=route[route.index("if end=='unload-reload':"):route.index("if end=='close-reopen':")]
 need(part.index("arm('native-unload'")<part.index("ctl('plugin','unload'")<part.index("arm('native-load'")<part.index("ctl('plugin','load'")<part.index("arm('reload'")<part.index("ctl('reload')"),'Original command/pre-binding chronology differs')
 runner=reader.read(stage/'run_native.py').decode();part=runner[runner.index('            if loaded:'):]
 need(part.index("arm('native-unload'")<part.index("ctl('plugin','unload',str(plugin))") and part.index("arm('probe-unload'")<part.index("ctl('plugin','unload',str(probe))")<part.index('complete(probe_ticket)')<part.index("'finalCompletedHelpers'"),'Final queue/archive ordering differs')
 return dict(postGateFrozenControlFlow=True,separatePostGateSnapshotRetained=False,initialFullSnapPrologue=prologue)

def expected_kinds(variant):
 result=['initial']
 for case in variant['cases']:
  if case['case'].endswith('unload-reload'):result+=['native-unload','native-load','reload']
  elif case['case'].endswith('reload'):result+=['reload']
 if variant.get('normalNativeUnload') is True:result+=['native-unload']
 if variant.get('actualProbeUnloadReply','').strip()=='ok':result+=['probe-unload']
 return result

def executor_forks(text,config):
 text=re.sub(r'\x1b\[[0-9;]*m','',text);lines=text.splitlines();result=[]
 for index,line in enumerate(lines):
  if '[executor] Executing ' not in line:continue
  command=line.split('[executor] Executing ',1)[1]
  if command!=config['helpers']['snap']['wrapper']+' hydrate':continue
  for cursor in range(index+1,min(index+13,len(lines))):
   if '[executor] Executing ' in lines[cursor]:break
   found=re.search(r'\[executor\] Process created with pid ([1-9][0-9]*)',lines[cursor])
   if found:result.append(dict(pid=int(found[1]),line=index+1,command=command));break
  else:raise ValueError('Exact hydrate executor fork identity missing')
 return lines,result

def replay_variant(stage,folder,variant,matrix,frozen,guard):
 archive=js(folder/'terminal-helpers/archive.json');config_raw=reader.read(folder/'terminal-helpers/helper-config.json');log_raw=reader.read(folder/'terminal-helpers/helper-events.jsonl');config=parse(config_raw);events=[parse(line) for line in log_raw.splitlines() if line.strip()]
 need(hashlib.sha256(config_raw).hexdigest()==archive['configSHA256'] and hashlib.sha256(log_raw).hexdigest()==archive['logSHA256'] and archive['completeEOF'] is True and archive['parseErrors']==[] and archive['events']==events,'Exact descriptor/fullEOF archive differs')
 starts,ends=normal_events(events);tickets=config['evaluationTickets']
 need(bool(tickets) and tickets==variant['evaluationTickets'] and len({t['nonce'] for t in tickets})==len(tickets) and config['activeEvaluation']==tickets[-1]['nonce'],'Missing/changed/duplicate actual tickets')
 need([t['kind'] for t in tickets]==expected_kinds(variant),'Actual original unload/load/explicit reload/final ticket order differs')
 need(variant['completedEvaluations']==list(range(1,len(tickets)+1)),'Missing/extra actual completion records')
 host=variant['hostEvidence'];need(same(config['compositor'],dict(pid=host['compositorPID'],start=host['compositorStart'])),'Selected compositor PID/start differs')
 configuration=config['evaluationConfiguration'];config_bytes=reader.read(folder/'host/runtime-archive/hyprland.lua')
 need(configuration['completeEOF'] is True and configuration['path']==host['compositorConfig'] and configuration['sha256']==host['compositorConfigSHA256']==hashlib.sha256(config_bytes).hexdigest() and guard['initialFullSnapPrologue'] in config_bytes.decode(),'Archived immutable startup configuration differs')
 need(configuration['sha256']==variant['reloadConfigurationWitness']['sha256'] and configuration['identity'][:2]==[variant['reloadConfigurationWitness']['device'],variant['reloadConfigurationWitness']['inode']],'Original configuration descriptor witness differs')
 source(stage/'helper_observer.py',config['helpers']['snap']['wrapperSHA256'],frozen);source(stage/'helper_observer.py',config['helpers']['shell']['wrapperSHA256'],frozen)
 source(matrix['pairedCloseHelper'],config['helpers']['snap']['actualSHA256'],frozen);source(stage/'payload/omarchy/bin/omarchy-shell',config['helpers']['shell']['actualSHA256'],frozen)
 authorizer=config['queryRoots']['harness'];need(authorizer['source']==str(stage/'run_native.py') and authorizer['argv'][1]==authorizer['source'] and Path(authorizer['argv'][0]).resolve()==Path(authorizer['executable']),'Exact authorizing harness source/argv differs')
 source(authorizer['source'],authorizer['sourceSHA256'],frozen);source(authorizer['executable'],authorizer['executableSHA256'],frozen);need(reader.gone(authorizer['identity']),'Actual harness PID/start remains live')
 prior=0;actual_keys=[];rows=[]
 for index,ticket in enumerate(tickets,1):
  need(ticket['serial']==index and ticket['armedNs']>prior and ticket['root']==authorizer and ticket['compositor']==config['compositor'] and ticket['instance']==config['instance'] and ticket['configuration']==configuration,'Ticket root/lifetime/serial/source/config chronology differs')
  ipc(ticket['armIPC'],config);required=keys(ticket);actual_keys+=required
  if ticket['kind']=='initial':need(ticket['command']==config['evaluationInitialCommand'] and ticket['artifact'] is None,'Initial full-paired-Snap command differs')
  elif ticket['kind']=='reload':need(ticket['command']==['reload'] and ticket['artifact'] is None,'Original explicit ctl reload differs')
  else:
   artifact=Path(matrix['probe'] if ticket['kind']=='probe-unload' else matrix['candidate']);material(ticket['artifact'],artifact,frozen);need(ticket['command']==['plugin','load' if ticket['kind']=='native-load' else 'unload',str(artifact)],'Exact actual artifact command differs')
  completed=js(folder/('evaluation-'+str(index)+'.json'))
  need(completed['ticket']==ticket and completed['actualOrdinal']==ticket['count'] and completed['expectedOperations']==required and completed['unloggedExactHelperProcesses']==[] and completed['allExpectedNormal'] is True and completed['fullEOF'] is True and completed['allExactProcessesGone'] is True and completed['terminalAuthority']==ticket['terminalAuthority'],'Incomplete/changed actual evaluation completion')
  ipc(completed['completionIPC'],config)
  need(events[:len(completed['events'])]==completed['events'],'Actual completion event prefix differs')
  selected=[row for row in starts if row['operation'] in required];need(len(selected)==len(required) and {r['operation'] for r in selected}==set(required),'Missing/duplicate per-occurrence callback')
  last=ticket['armedNs']
  for start in selected:
   end=reader.one(ends,'operation',start['operation']);ordinal=int(start['operation'].rsplit(':',2)[1]);base=start['operation'].rsplit(':',1)[1]
   need(start['timeNs']>=ticket['armedNs'] and start['evaluationEnvironment']==dict(zip(ENV,[ticket['nonce'],ticket['kind'],str(ticket['count']),str(ordinal)])),'Actual child nonce/kind/count/ordinal differs or precedes arm')
   need(start['class']=='compositor' and start['queryRoot'] is None and start['helper']==('snap' if base=='hydrate' else 'shell'),'Actual callback role differs')
   if base=='hydrate':need(start['args']==['hydrate'],'Exact hydrate argv differs')
   else:
    args=start['args'];need(len(args)==7 and args[:3]==['hoskinson.windows','fileDrag','false'],'Exact inactive relay argv differs')
    for n,value in enumerate(args[3:]):need(isinstance(value,str) and re.fullmatch('0|-?[1-9][0-9]*',value) and -(1<<63)<=int(value)<(1<<63) and (n!=3 or int(value)>=0),'Exact signed bounded inactive relay payload differs')
   ancestry=start['ancestry'];need(1<=len(ancestry)<=2 and same(ancestry[-1],config['compositor']) and start['wrapper']['parent']==ancestry[0]['pid'] and (len(ancestry)==1 or ancestry[0]['parent']==config['compositor']['pid']) and start['delegate']['parent']==start['wrapper']['pid'],'Genuine compositor/optional-shell/helper ancestry differs')
   helper=config['helpers'][start['helper']];need(start['actual']==helper['actual'] and start['actualSHA256']==helper['actualSHA256'],'Actual delegate source differs');ipc(start['ipc'],config)
   last=max(last,end['timeNs'])
  prior=last
  if ticket['terminalAuthority']:
   need(ticket['kind'] in ('native-unload','probe-unload') and index>len(tickets)-2 and all(variant['nativeUnloadOrdering'].get(k) is True for k in ('genuineInputsReleasedNormally','normalToolkitLifetimesGone','normalShellServiceLifetimesGone','allExactHelperProcessesGone','clientListEmpty')),'Terminal authority bypassed actual owned lifetime ordering')
  else:need(index<=len(tickets)-2,'Final unload lacks explicit terminal authority')
  rows.append(dict(serial=index,nonce=ticket['nonce'],kind=ticket['kind'],actualOrdinal=completed['actualOrdinal'],normalCallbacks=len(selected),lastTerminalNs=last,terminalAuthority=ticket['terminalAuthority']))
 extra=[row['operation'] for row in starts if row.get('class','compositor')=='compositor' and row['operation'].startswith('evaluation:')];need(len(extra)==len(actual_keys) and set(extra)==set(actual_keys),'Extra or missing actual evaluation callback')
 need(set(config['allowed'])==set(actual_keys)|{row['operation'] for row in starts if row.get('class','compositor')=='compositor' and row['operation'].startswith('forget-closed:')},'Missing/unknown final helper obligation')
 final=js(folder/'final-completed-helpers.json');need(final['events']==events and final['config']==config and final['allNormal'] is True and final['allExactProcessesGone'] is True,'Final queue sample differs from durable archive')
 text=reader.read(folder/'host/hyprland.log').decode();need('Unexpected extra private Lua evaluation' not in text and 'Exact private evaluation nonce required' not in text and 'Exact private evaluation command required' not in text and 'Exact private evaluation ordinal required' not in text,'Actual late/extra/unknown evaluation prologue fault retained')
 lines,forks=executor_forks(text,config);hydrates=[row for row in starts if row['operation'] in actual_keys and row['helper']=='snap']
 need(len(forks)==len(hydrates),'Extra/missing actual hydrate executor fork')
 used=[]
 for hydrate in sorted(hydrates,key=lambda row:row['timeNs']):
  candidates=[f for f in forks if f['pid'] in [hydrate['wrapper']['pid']]+[a['pid'] for a in hydrate['ancestry'][:-1]]];need(len(candidates)==1,'Actual callback lacks exact native executor PID');used.append(candidates[0]['line'])
 need(used==sorted(used),'Actual native callback order differs')
 # Genuine load/unload log ordering independently corroborates command kinds;
 # exact ctl argument/reply provenance remains frozen source + retained ACKs.
 actions=[(i+1,'native-load' if 'Plugin hyprbars loaded.' in line else 'native-unload' if 'Plugin hyprbars unloaded.' in line else 'probe-unload') for i,line in enumerate(lines) if 'Plugin hyprbars loaded.' in line or 'Plugin hyprbars unloaded.' in line or 'Plugin toolkit-held-probe unloaded.' in line or 'Plugin toolkit_held_probe unloaded.' in line]
 expected_native=['native-load']+[t['kind'] for t in tickets if t['kind'] in ('native-load','native-unload','probe-unload')]
 need([kind for _,kind in actions]==expected_native,'Actual native load/unload log chronology differs')
 return dict(tickets=rows,normalCallbacks=len(actual_keys),actualNativeActions=actions,actualHydrateExecutorLines=used,postGateEvidence='frozen exact gate codepath plus captured reservation selectors and exact normal delegate terminal',separatePostGateSnapshotRetained=False,producerVariantResult=variant['result'],featureFailureErased=False)

def audit(stage,attempt):
 frozen=js(stage/'frozen-inputs.json');report=js(attempt/'report.json');matrix=js(stage/'matrix.json');checks={};errors={};rows=[]
 def check(name,function):
  try:function();checks[name]=True
  except Exception as error:checks[name]=False;errors[name]=repr(error)
 check('wholeFrozenBytesModesLinks',lambda:need(all(reader.digest(p)==(h,frozen['inputModes'][p]) for p,h in frozen['inputs'].items()) and all(Path(p).is_symlink() and os.readlink(p)==t for p,t in frozen['symlinks'].items()),'Frozen closure changed'))
 guard=None
 try:guard=source_guards(stage,frozen);checks['exactFrozenPrecommandAndPostgateControlFlow']=True
 except Exception as error:checks['exactFrozenPrecommandAndPostgateControlFlow']=False;errors['sourceGuards']=repr(error)
 for variant in report['variants']:
  try:row=replay_variant(stage,attempt/variant['variant'],variant,matrix,frozen,guard);checks[variant['variant']+'ExactEvaluationReplay']=True;rows.append(dict(variant=variant['variant'],**row))
  except Exception as error:checks[variant['variant']+'ExactEvaluationReplay']=False;errors[variant['variant']]=repr(error)
 failure=report['result']!='pass' or any(c['result']!='pass' for v in report['variants'] for c in v['cases']) or bool(errors)
 checks['terminalAuthorityCannotEraseFeatureFailure']=not failure or report['result']=='fail'
 checks['actualVariantPresent']=bool(report['variants'])
 return dict(result='pass' if all(checks.values()) else 'fail',checks=checks,errors=errors,rows=rows,producerResult=report['result'],producerReachedCases=sum(len(v['cases']) for v in report['variants']),sourceManifestSHA256=reader.digest(stage/'frozen-inputs.json')[0],auditorSHA256=reader.digest(BASE/'audit.py')[0],readerSHA256=reader.digest(READER)[0],nativeCommands=False,mainWrites=False,fullHeld52Accepted=False,boundary='Evaluation ticket/queue evidence only. Existing whole52 terminal and retirement auditors remain mandatory and failures preserved. Root command timing and postgate selector checks rely on exact frozen code paths plus retained actual callbacks/ACKs; no separate command-send or postgate snapshot is fabricated.')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stage',type=Path,required=True);parser.add_argument('--attempt',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();stage=args.stage.resolve();attempt=args.attempt.resolve();output=args.output.absolute()
 need(attempt.parent==stage and attempt.name.startswith('attempt-') and output.parent==attempt,'Owned additive terminal artifact required')
 fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  try:result=audit(stage,attempt)
  except BaseException:result=dict(result='fail',error=traceback.format_exc(),nativeCommands=False,mainWrites=False,fullHeld52Accepted=False)
  with os.fdopen(fd,'w',closefd=False) as stream:json.dump(result,stream,indent=2);stream.write('\n');stream.flush();os.fsync(fd)
 finally:os.close(fd)
 print(json.dumps(dict(result=result['result'],artifact=str(output))));return int(result['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
