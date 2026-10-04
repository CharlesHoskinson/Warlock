import importlib.util,json,os,shutil,subprocess,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-registration-query-runtime-v585'
spec=importlib.util.spec_from_file_location('registration_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host);host.original.qa.require_qa_scope()
sys_adapter=REPO/'implementation/elm-stable-surface-publication-v521/adapter'
import sys
sys.path.insert(0,str(sys_adapter));from endpoint import start_time,binding,exact,canonical
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-registration-'+str(time.time_ns()))
r={'passed':False,'nativeAcceptance':False,'scope':'Private native read-only registration protocol only; no Unknown settlement/durable retirement/window-system acceptance','mainDesktopActions':False,'checks':[]};s=None;loaded=False;peers=[];counters={};commands=[]
def check(name,value,**evidence):r['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
def exchange(index,operation,request=None):
 process=peers[index];assert process.poll() is None
 counters[index]=counters.get(index,0)+1;seq=counters[index];command={'sequence':seq,'operation':operation}
 if request is not None:command['request']=request
 control=OUTPUT/('control-'+str(index)+'.json');temp=control.with_suffix('.tmp');temp.write_text(json.dumps(command)+'\n');temp.replace(control);commands.append({'peer':index,**command})
 if operation=='quit':return
 until=time.monotonic()+6;output=OUTPUT/('reply-'+str(index)+'.json')
 while time.monotonic()<until:
  s.guard();assert process.poll() is None
  if output.exists():
   row=json.loads(output.read_text())
   if row['sequence']==seq:r.setdefault('wire',[]).append({'peer':index,'request':command,'reply':row});return row
  time.sleep(.01)
 raise RuntimeError('Unchanged observation deadline')
def payload(current,queried,request='1'):return {'protocolVersion':3,'kind':'binding-registration-request','binding':current,'queriedBinding':queried,'requestId':request}
def query(index,current,queried,expected,request='1'):
 reply=exchange(index,'request',payload(current,queried,request));assert reply['ok'];value=reply['response'];exact(value,['protocolVersion','kind','registrationProtocol','binding','queriedBinding','requestId','registered']);assert value['kind']=='binding-registration' and value['registrationProtocol']==1 and type(value['registrationProtocol']) is int and type(value['registered']) is bool and binding(value['binding'])==current and binding(value['queriedBinding'])==queried and canonical(value['requestId'])==request
 return value['registered']==expected
try:
 preflight=json.loads((ROOT/'qa/preflight.json').read_text());assert preflight['passed']
 for path,digest in preflight['inputs'].items():assert host.digest(path)==digest,path
 r['preflightSHA256']=host.digest(ROOT/'qa/preflight.json');manifest=json.loads((CORE/'qa/build-pair-manifest.json').read_text());pair=manifest['nativePair'];plugin=pair['plugin']['path'];r['pair']=pair
 for rel,digest in manifest['files'].items():assert host.digest(CORE/rel)==digest
 for row in pair.values():assert host.digest(row['path'])==row['sha256']
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),1600,1000,b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n',mesa_vendor=True) as s:
  try:
   check('owningPluginLoaded',s.ctl('plugin','load',plugin).strip()=='ok');loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   mapped=Path('/proc/'+str(native['pid'])+'/maps').read_text();check('exactPluginMapped',any(line.split()[-1]==plugin for line in mapped.splitlines() if line.split()))
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256'],'adapter':str(sys_adapter)}
   path=OUTPUT/'config.json';path.write_text(json.dumps(config));path.chmod(0o600)
   for index in range(2):peers.append(s.host.launch('registration-peer-'+str(index),['/usr/bin/python3','-B',str(ROOT/'qa/peer.py'),str(path),str(OUTPUT/('control-'+str(index)+'.json')),str(OUTPUT/('reply-'+str(index)+'.json'))],env=s.env))
   a=exchange(0,'hello');b=exchange(1,'hello');assert a['ok'] and b['ok'];old=binding(a['response']['binding']);current=binding(b['response']['binding']);check('distinctLivePeerGrants',a['pid']!=b['pid'] and old['lifetime']==current['lifetime'] and old['session']!=current['session'],old=old,current=current)
   check('ownRegisteredGrant',query(0,old,old,True))
   check('otherLivePeerSurvivesAttach',query(1,current,old,True))
   check('currentGrantStillRegistered',query(1,current,current,True))
   again=exchange(0,'hello');assert again['ok'];new=binding(again['response']['binding']);check('samePeerAdvancesFrontend',new['lifetime']==old['lifetime'] and new['session']==old['session'] and int(new['frontend'])==int(old['frontend'])+1)
   check('oldExactFrontendNoLongerRegistered',query(1,current,old,False))
   check('replacementFrontendRegistered',query(1,current,new,True))
   refusal=exchange(0,'request',payload(old,old));check('oldFrontendCannotQuery',not refusal['ok'] and refusal['reason']=='binding-mismatch')
   refusal=exchange(1,'request',payload(new,old));check('otherPeersCurrentGrantCannotAuthenticateCaller',not refusal['ok'] and refusal['reason']=='binding-mismatch')
   foreign={**old,'lifetime':str(int(old['lifetime'])-1) if old['lifetime']!='1' else '2'};refusal=exchange(1,'request',payload(current,foreign));check('foreignNativeLifetimeRefused',not refusal['ok'] and refusal['reason']=='registration-lifetime-mismatch')
   absent={**current,'frontend':'18446744073709551615'};check('absentTupleAndMaxRequestEcho',query(1,current,absent,False,'18446744073709551615'))
   invalid=[('extraField',{**payload(current,old),'extra':True}),('missingRequest',{k:v for k,v in payload(current,old).items() if k!='requestId'}),('zeroFrontend',payload(current,{**old,'frontend':'0'})),('noncanonicalFrontend',payload(current,{**old,'frontend':'01'})),('integerFrontend',payload(current,{**old,'frontend':1})),('overflowRequest',payload(current,old,'18446744073709551616'))]
   for name,request in invalid:
    refusal=exchange(1,'request',request);check(name+'Refused',not refusal['ok'],reply=refusal)
   check('queriesPreserveBothCurrentGrants',query(1,current,new,True) and query(1,current,current,True))
   check('readOnlyQueriesLeaveNativeClientsEmpty',s.data('clients')==[])
   r['passed']=True
  finally:
   for index,process in enumerate(peers):
    if process.poll() is None:exchange(index,'quit');process.wait(timeout=5)
    check('registeredPeerNormalExit'+str(index),process.returncode==0,exitCode=process.returncode)
   check('clientsEmptyBeforePluginUnload',s.data('clients')==[])
   if loaded:check('owningPluginNormallyUnloaded',s.ctl('plugin','unload',plugin).strip()=='ok');loaded=False
except Exception as error:r.update(passed=False,error=repr(error),traceback=traceback.format_exc())
r['commands']=commands;r['privateHost']=s.evidence if s else None;r['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'));r['passed']=r['passed'] and r['cleanupPassed']
if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',symlinks=True)
r['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
