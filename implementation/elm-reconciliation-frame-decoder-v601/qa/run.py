#!/usr/bin/env python3
import copy,hashlib,json,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('tests-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NATIVE=REPO/'implementation/elm-grant-retirement-native-v596/qa/native-1791146569027803533/report.json'
UNKNOWN=REPO/'implementation/elm-unknown-reservation-reproducer-v575/qa/replay-1791143832598854566/frames.json'
original=json.loads(NATIVE.read_text());rawunknown=json.loads(UNKNOWN.read_text())
proof=next(c['reply']['response'] for c in original['wire'] if isinstance(c.get('reply'),dict) and c['reply'].get('response',{}).get('kind')=='binding-retirement' and c['reply']['response'].get('operation')=='retire' and c['reply']['response'].get('requestId')=='23')
(OUT/'captured596-proof.json').write_text(json.dumps(proof,indent=2)+'\n');shutil.copy2(UNKNOWN,OUT/'captured573-unknown-source.json');shutil.copy2(NATIVE,OUT/'captured596-report.json')
intent=copy.deepcopy(rawunknown['intent']);intent['context']['lifetime']=proof['queriedBinding']['lifetime'];intent['context']['epoch']=proof['queriedBinding']['frontend']
record={'schema':2,'effectProtocol':1,'binding':proof['queriedBinding'],'intent':intent,'status':'Unknown'}
act={'lifetime':proof['binding']['lifetime'],'epoch':proof['binding']['frontend'],'output':'7','revision':'37'}
geo={**act,'revision':'101'}
expected={'currentBinding':proof['binding'],'record':record,'proofRequestId':proof['requestId'],'actionRequestId':'91','geometryRequestId':'93','actionContext':act,'geometryContext':geo}
release={'id':'0123456789abcdef'*4,'proof':proof,'observation':{'actionRequestId':'91','geometryRequestId':'93','actionContext':act,'geometryContext':geo}}
frame={'protocolVersion':3,'kind':'host-reservation-released','binding':proof['binding'],'record':record,'release':release}
unknown={'protocolVersion':3,'kind':'host-reservation-unknown','binding':proof['binding'],'record':record}
cases=[]
def add(name,f,ok=False,e=None,released=True):cases.append({'name':name,'frame':copy.deepcopy(f),'expected':copy.deepcopy(e or expected),'released':released,'expectedOk':ok})
def changed(obj,path,value):
 obj=json.loads(json.dumps(obj));o=obj
 for p in path[:-1]:o=o[p]
 o[path[-1]]=value;return obj
add('normalized-cross-campaign-release',frame,True)
add('unknown-retains-old-binding',unknown,True,released=False)
add('proof-observe-retired',changed(frame,['release','proof','operation'],'observe'),True)
geometry=copy.deepcopy(frame);geometry['record']['effectProtocol']=2;geometry['record']['intent']['operation']='maximize';geometry_expected={**expected,'record':geometry['record']};add('geometry-record-unknown',geometry,True,e=geometry_expected)
# Positive boundary changes keep each independent domain internally correlated.
maximum='18446744073709551615';boundary=copy.deepcopy(frame);boundary_expected=copy.deepcopy(expected)
for root in [boundary,boundary_expected]:
 if root is boundary:
  root['record']['intent']['request']=maximum;root['record']['intent']['generation']=maximum
  root['release']['proof']['sequence']=maximum
 else:root['record']['intent']['request']=maximum;root['record']['intent']['generation']=maximum
add('max-uint64-independent-history-sequence',boundary,True,e=boundary_expected)
for path in [
 ['binding','session'],['release','proof','binding','session'],['release','proof','queriedBinding','session'],['release','proof','requestId'],['release','observation','actionRequestId'],['release','observation','geometryRequestId'],
 ['record','binding','frontend'],['record','intent','request'],['record','intent','generation'],['record','intent','incarnation'],['record','intent','context','lifetime'],['record','intent','context','epoch'],['record','intent','context','output'],['record','intent','context','revision'],
 ['release','observation','actionContext','lifetime'],['release','observation','actionContext','epoch'],['release','observation','actionContext','output'],['release','observation','actionContext','revision'],
 ['release','observation','geometryContext','lifetime'],['release','observation','geometryContext','epoch'],['release','observation','geometryContext','output'],['release','observation','geometryContext','revision']]:
 add('foreign-or-stale-'+'-'.join(path),changed(frame,path,'9'))
for path in [['record','intent','request'],['record','intent','generation'],['record','intent','incarnation'],['release','proof','sequence'],['release','proof','requestId'],['release','observation','actionRequestId'],['release','observation','geometryRequestId'],['release','observation','actionContext','revision'],['release','observation','geometryContext','output'],['binding','session']]:
 for bad in [True,12,0,'0','01','-1','18446744073709551616','']:
  add('counter-shape-'+'-'.join(path)+'-'+repr(bad),changed(frame,path,bad))
for path,bads in [(['protocolVersion'],[True,2,'3']),(['kind'],['host-reservation-unknown','other']),(['record','schema'],[True,1,'2']),(['record','effectProtocol'],[True,0,3,'1']),(['record','status'],['Pending','Committed','Refused','Cancelled']),(['record','intent','operation'],['maximize','unsupported']),(['release','proof','grantState'],['Registered','Future','Unknown']),(['release','proof','operation'],['settle','']),(['release','proof','retirementProtocol'],[True,2]),(['release','proof','kind'],['effect-outcome']),(['release','id'],['a'*63,'a'*65,'G'*64,'A'*64,True,'g'*64])]:
 for bad in bads:add('enum-shape-'+'-'.join(path)+'-'+repr(bad),changed(frame,path,bad))
for path in [[],['record'],['record','binding'],['record','intent'],['record','intent','context'],['release'],['release','proof'],['release','observation'],['release','observation','actionContext']]:
 altered=copy.deepcopy(frame);o=altered
 for part in path:o=o[part]
 o['unexpected']=True;add('extra-fields-'+str(path),altered)
 missing=copy.deepcopy(frame);o=missing
 for part in path:o=o[part]
 del o[next(iter(o))];add('missing-fields-'+str(path),missing)
add('expected-output-scope-mismatch',frame,e=changed(expected,['geometryContext','output'],'9'))
add('expected-current-epoch-mismatch',frame,e=changed(expected,['actionContext','epoch'],'9'))
add('unknown-foreign-current-binding',changed(unknown,['binding','session'],'9'),released=False)
add('unknown-invalid-old-authority',changed(unknown,['record','intent','context','epoch'],'9'),released=False)
add('unknown-nonunknown-status',changed(unknown,['record','status'],'Committed'),released=False)
inputs=OUT/'inputs';shutil.copytree(ROOT/'src',inputs/'src');shutil.copy2(ROOT/'elm.json',inputs/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',inputs/'src/Probe.elm')
(OUT/'cases.json').write_text(json.dumps({'cases':cases},indent=2)+'\n')
commands=[]
for name,command,cwd in [('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','--optimize','src/Probe.elm','--output='+str(OUT/'worker.js')],inputs),('test',['node',str(ROOT/'qa/probe.cjs'),str(OUT/'worker.js'),str(OUT/'cases.json'),str(OUT/'results.json')],ROOT)]:
 p=subprocess.run(command,cwd=cwd,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);commands.append({'command':command,'cwd':str(cwd),'exitCode':p.returncode});assert p.returncode==0,p.stderr.decode()[-2500:]
results=json.loads((OUT/'results.json').read_text());assert len(results)==len(cases)
checks=[]
for case,result in zip(cases,results):
 good=result['ok']==case['expectedOk'] and (not result['ok'] or (result['historicalStatus']=='Unknown' and result['intent']==case['frame']['record']['intent'] and result['oldBinding']==case['frame']['record']['binding']))
 checks.append({'name':case['name'],'passed':good,'expectedOk':case['expectedOk'],'result':result})
report={'passed':all(c['passed'] for c in checks),'nativeAcceptance':False,'scope':'Isolated pure typed frame decoding/correlation only; no production policy, effects, backend authentication or fsync acceptance','checks':checks,'commands':commands,'syntheticNormalization':{'sourceProof':str(NATIVE),'sourceProofSHA256':sha(NATIVE),'sourceUnknown':str(UNKNOWN),'sourceUnknownSHA256':sha(UNKNOWN),'mapping':'596 retired queriedBinding becomes old record binding;573 request12 intent lifetime/epoch normalized to that binding. Independent current action/geometry contexts and IDs are synthetic declared expectations, not one captured campaign.'},'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts}}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'cases':len(cases),'report':str(OUT/'report.json')}));raise SystemExit(not report['passed'])
