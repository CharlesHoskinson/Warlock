import hashlib,json,math,re,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];native=next((REPO/'implementation/elm-surface-publication-trace-native-v533/qa').glob('native-*/report.json'));n=json.loads(native.read_text());assert n['passed'] and n['cleanupPassed'] and len(n['checks'])==89
log=native.parent/'native-evidence/elm-webview.log';lines=log.read_text(errors='strict').splitlines()
def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate')
  d[k]=v
 return d
def decode(s):return json.loads(s,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite')))
def uint(s):
 if not re.fullmatch(r'0|[1-9][0-9]*',s) or int(s)>2**64-1:raise ValueError('counter')
 return int(s)
def bridge(line):
 m=re.fullmatch(r'qa-bridge-input: origin=(controller|bar|popup|unregistered) view=([0-9]+) generation=([0-9]+) json=(.*)',line)
 if not m:raise ValueError('header')
 role,view,generation,wire=m.groups();view=uint(view);generation=uint(generation);value=decode(wire)
 if type(value) is not dict or value.get('kind') not in ('view-commit','surface-context'):raise ValueError('message')
 if role=='bar' and (view==0 or generation==0):raise ValueError('view')
 return {'origin':role,'view':view,'generation':generation,'message':value}
def pointer(line):
 if not line.startswith('qa-pointer-proof: '):raise ValueError('proof prefix')
 fields=dict(item.split('=',1) for item in line.split(': ',1)[1].split());expected=['type','button','time','view','generation','publication','lease','epoch','captured','pressed','available','x','y']
 if set(fields)!=set(expected):raise ValueError('proof schema')
 values={k:uint(v) for k,v in fields.items() if k not in ['x','y']};values.update({k:float(fields[k]) for k in ['x','y']})
 if values['type'] not in [4,7] or not values['view'] or not values['generation'] or values['pressed'] not in [0,1] or values['available'] not in [0,1] or any(not math.isfinite(values[k]) for k in ['x','y']):raise ValueError('proof values')
 return values
bridges=[(i,bridge(l)) for i,l in enumerate(lines) if l.startswith('qa-bridge-input: ')];proofs=[(i,pointer(l)) for i,l in enumerate(lines) if l.startswith('qa-pointer-proof: ')];frames={}
for i,b in bridges:
 if b['message']['kind']=='view-commit':
  assert b['origin']=='controller';packet=b['message'];assert set(packet)=={'viewProtocol','kind','projection','requests','focus'} and packet['viewProtocol']==1;frame=packet['projection']['frame'];uint(frame['publication']);uint(frame['lease']);frames[frame['publication']]=(i,packet)
joined=[]
for i,p in proofs:
 if p['type']!=7 or p['button']!=3 or p['available']!=1:continue
 stop=next((j for j,_ in proofs if j>i),len(lines));candidate=next(((j,b) for j,b in bridges if i<j<stop and b['message']['kind']=='surface-context' and b['message']['trigger']=='pointer'),None)
 if candidate is None:continue
 j,b=candidate;message=b['message'];matching=uint(message['publication'])==p['publication'] and uint(message['lease'])==p['lease'];frame=frames.get(str(p['publication']));assert frame is not None
 if matching:
  controls=frame[1]['projection']['frame']['bar' if message['surface']=='bar' else 'popup'];assert any(c['id']==message['id'] and c['enabled'] is True for c in controls)
  assert type(message['x']) is int and type(message['y']) is int and (message['x']-p['x'])**2+(message['y']-p['y'])**2<=2
 commits=[l for l in lines[i+1:j] if l.startswith('surface-commit: ')];joined.append({'proofLine':i+1,'messageLine':j+1,'proof':p,'message':message,'matchedStamp':matching,'interveningNativeCommits':commits})
assert len(bridges)>0 and len(proofs)>0 and len(joined)>0
negatives=[('duplicate',lambda:decode('{"x":1,"x":2}')),('nonfinite',lambda:decode('{"x":NaN}')),('overflow',lambda:uint('18446744073709551616')),('leadingzero',lambda:uint('01')),('wrongrole',lambda:bridge('qa-bridge-input: origin=wrong view=1 generation=1 json={}'))]
for name,call in negatives:
 try:call()
 except ValueError:continue
 raise AssertionError(name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'passed':True,'scope':'Actual QA native trace decoded and correlated to admitted physical release stamps/full frame controls; no deterministic504 reproduction or hardware acceptance','nativeReport':str(native),'nativeReportSHA256':sha(native),'log':str(log),'logSHA256':sha(log),'bridgeInputCount':len(bridges),'pointerProofCount':len(proofs),'receivedCommitCount':sum(b['message']['kind']=='view-commit' for _,b in bridges),'correlatedPointerContexts':joined,'decoderNegativeControls':len(negatives),'pointerRaceCausallyResolved':False,'fullReleaseAccepted':False};p=ROOT/'qa/report.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'bridgeInputs':len(bridges),'pointerProofs':len(proofs),'correlatedContexts':len(joined),'interveningCommitContexts':sum(bool(j['interveningNativeCommits']) for j in joined),'report':str(p)}))
