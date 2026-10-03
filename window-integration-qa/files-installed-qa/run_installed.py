#!/usr/bin/env python3
"""Fresh installed-source Qt fixtures, private offscreen only; no original process input."""
from pathlib import Path
import ast,datetime,hashlib,json,os,shutil,signal,subprocess,time
from prepare_fixture import prepare
B=Path(__file__).resolve().parent;LIVE=Path.home()/'.local/share/omarchy-files'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 m=json.loads((B/'frozen-sources.json').read_text())
 for row in m['files']:assert digest(Path(row['path']))==row['sha256'],row['path']
 return m
verify();manifest_bytes=(B/'frozen-sources.json').read_bytes();os.umask(0o077)
O=B/('attempt-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S-%f'));O.mkdir(mode=0o700)
report={'scope':'Actual installed Files sources copied into private offscreen Qt fixtures; no original launch/kill/input, native reader or physical hardware claim','checks':[],'result':'pending','attempt':str(O),'sourceManifestSHA256':digest(B/'frozen-sources.json'),'reports':{}}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name

def evaluate_editable(actual):
 baseline=json.loads((B/'editable-baseline-counterexample.json').read_text());base={(c['item'],c['context'],c['operation']):c for c in baseline['cases']};checks=[]
 checks.append({'name':'actual native editable fixture completed normally','passed':not actual.get('error') and actual.get('exitCode')==-15 and len(actual.get('cases',[]))==88})
 for c in actual.get('cases',[]):
  key=(c['item'],c['context'],c['operation']);old=base[key]
  refusal=c['context'] in ('hidden','disabled','modalBackground') or c['context']=='readOnly' and c['operation'] in ('delete','insert','replace','setValue')
  valid=not c['changed'] and c['before']==c['after'] if refusal else c['before']==old['before'] and c['after']==old['after']
  checks.append({'name':'/'.join(key)+(' refuses mutation' if refusal else ' preserves native positive behavior'),'passed':valid})
 checks.append({'name':'destroyed native text peer is defunct','passed':not actual.get('destroyedPeer',{}).get('interfaceFound',True) and not actual.get('destroyedPeer',{}).get('objectAlive',True)})
 return checks

def evaluate_routing(actual,toggle):
 checks=[{'name':'actual routing fixture normal','passed':not actual.get('error') and actual.get('exitCode')==-15}]
 for mode in ('list','grid'):
  trace={r['event']:r for r in actual.get('trace',[])}
  for step in (1,2):
   row=trace.get(f'{mode} Down {step}',{});identity=row.get('focusIdentity','');selected=row.get('sel',[])
   checks.append({'name':f'{mode} Down {step} focus/selection captured path agrees','passed':identity.startswith('file:') and selected==[Path(identity.removeprefix('file:')).name]})
  row=trace.get(f'{mode} F2',{});prompt=row.get('prompt',{});selected=row.get('sel',[]);identity=row.get('focusIdentity','')
  checks.append({'name':f'{mode} F2 captures selected actual source','passed':prompt.get('visible') and len(selected)==1 and prompt.get('text')==selected[0] and Path((prompt.get('payload') or {}).get('path','')).name==selected[0]})
  checks.append({'name':f'{mode} Shift Down preserves range','passed':len(trace.get(f'{mode} Shift Down',{}).get('sel',[]))>=2})
 checks.append({'name':'actual raw Toggle fixture normal','passed':not toggle.get('error') and toggle.get('exitCode')==-15 and len(toggle.get('observations',[]))==4})
 for row in toggle.get('observations',[]):checks.append({'name':'raw retained current '+row['context']+' Toggle authority','passed':row['changed']==(row['context']=='visible')})
 return checks

child=None
try:
 check('installed Qt private-interface version matches native build',subprocess.check_output(['pkg-config','--modversion','Qt6Quick'],text=True).strip()=='6.11.2')
 for name in ('keys','routing','toggle','editable'):
  folder=O/name;folder.mkdir(mode=0o700);app=prepare(folder)
  template=(B/(name+'_template.py')).read_text()
  template=template.replace("B/'qa-app'","B/'app'").replace("B/'isolated-home'","B/'home'").replace("B/'isolated-state'","B/'state'").replace("B/'isolated-cache'","B/'cache'")
  template=template.replace("Path('/home/hoskinson/window-integration-qa/files-keyboard/editable-stage-v6/isolated-home/fixture')","(B/'home/fixture')").replace("Path('/home/hoskinson/window-integration-qa/files-keyboard/editable-stage-v6/isolated-home')","(B/'home')").replace("Path.home()/'window-integration-qa/files-keyboard/editable-stage-v6/isolated-home'","(B/'home')")
  template=template.replace("Path('/home/hoskinson/window-integration-qa/files-keyboard/guard-stage/isolated-home')",repr(str(B/'home-template')))
  template=template.replace('files-retained-qa','files-keyboard-qa').replace('V5 and staged real QML instantiate','Installed V7 real QML/native V6 instantiate')
  if name!='editable':shutil.copytree(B/'home-template',folder/'home')
  source=folder/'run.py';source.write_text(template);ast.parse(template)
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');log=(folder/'runner.log').open('w');child=subprocess.Popen(['python3',str(source)],stdout=log,stderr=log,env=env,start_new_session=True)
  forced=False
  try:code=child.wait(timeout=90)
  except subprocess.TimeoutExpired:
   forced=True;os.killpg(child.pid,signal.SIGTERM)
   try:code=child.wait(timeout=8)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait(timeout=4)
  log.close();check(name+' owned runner exits without timeout',not forced and code==0)
  path=folder/('offscreen-keys-report.json' if name=='keys' else 'report.json');actual=json.loads(path.read_text());report['reports'][name]={'path':str(path),'sha256':digest(path),'actual':actual}
  provenance=json.loads((folder/'fixture-provenance.json').read_text());check(name+' actual executed copied source bytes unchanged',all(digest(app/p)==h for p,h in provenance['executedFixtureBytes'].items()))
  if name=='keys':check('actual installed keyboard/focus 58 gates',actual.get('result')=='pass' and len(actual['checks'])==58)
 editable=evaluate_editable(report['reports']['editable']['actual']);routing=evaluate_routing(report['reports']['routing']['actual'],report['reports']['toggle']['actual'])
 for label,checks in [('editable',editable),('routing',routing)]:
  report[label+'Checks']=checks;check('actual installed '+label+' gates',all(c['passed'] for c in checks))
except Exception as error:report['error']=repr(error)
finally:
 if child and child.poll() is None:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=8)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=4);report['forcedFinalCleanup']=True
 try:verify();report['frozenSourcesAfterExact']=True
 except Exception as error:report['frozenSourcesAfterExact']=False;report['sourceError']=repr(error)
 report['manifestBytesExact']=(B/'frozen-sources.json').read_bytes()==manifest_bytes
 report['result']='pass' if not report.get('error') and not report.get('forcedFinalCleanup') and all(c['passed'] for c in report['checks']) and report['frozenSourcesAfterExact'] and report['manifestBytesExact'] else 'fail'
 p=O/'report.json';p.write_text(json.dumps(report,indent=2)+'\n');p.chmod(0o600)
 print(json.dumps({'result':report['result'],'sourceChecks':len(report['checks']),'keyboardChecks':len(report.get('reports',{}).get('keys',{}).get('actual',{}).get('checks',[])),'routingChecks':len(report.get('routingChecks',[])),'editableChecks':len(report.get('editableChecks',[])),'report':str(p),'reportSHA256':digest(p),'error':report.get('error')}))
raise SystemExit(report['result']!='pass')
