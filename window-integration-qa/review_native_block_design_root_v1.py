#!/usr/bin/python3
"""Review source-supported monocle blocker protocol, without native authority."""
import datetime,hashlib,json,os,re,stat
from pathlib import Path
from qa_launch import require_qa_scope
scope=require_qa_scope();Q=Path('/home/hoskinson/window-integration-qa');B=Path('/home/hoskinson/window-behavior-spec/pin-native-input-block-v1-design')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ready=B/'DESIGN_READY-final.json';assert sha(ready)=='19098f9f1123ae1eeb206fbcfe0829678571ead8618923b8f339917360a13b2b'
r=json.loads(ready.read_bytes())
for name,w in r['proposalFiles'].items():assert sha(B/name)==w['sha256'] and stat.S_IMODE((B/name).stat().st_mode)==w['mode']
origins=json.loads((B/'SOURCE_ORIGINS.json').read_bytes())
for path,w in origins.items():assert sha(path)==w['sha256'] and stat.S_IMODE(Path(path).stat().st_mode)==w['mode']
proof=json.loads((B/'FORMAL_PROOF.json').read_bytes())
for x in proof['commands']:assert x['exitCode']==0 and sha(x['log'])==x['logSHA256']
named=next(x for x in proof['commands'] if 'test' in x['argv'])
text=Path(named['log']).read_text();actual=re.findall(r'^\s*ok ([A-Za-z_][A-Za-z0-9_]*) passed \d+ test\(s\)',text,re.M)
assert len(actual)==14 and set(actual)==set(proof['sourceNamed']) and '14 passing' in text and '--match' in named['argv']
assert sha(B/'input_block.qnt')==proof['sourceModelSHA256']=='bab5212c8d081b8954b4a5504cebbb3775b6facc37e85f957577e269f8fab895'
assert r['nativeReachabilityProved'] is False and r['runtimeImplemented'] is False
parent=Q/'pin-max-native-campaign-b-v4';assert sha(parent/'frozen-inputs.json')==r['currentBv4FrozenUnchanged']['sha256'] if isinstance(r['currentBv4FrozenUnchanged'],dict) else r['currentBv4FrozenUnchanged'] is True
out=Q/'pin-native-block-root-source-grant-v1.json'
row=dict(result='pass',schema='root-native-input-block-source-grant-v1',observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=scope,
    designReadySHA256=sha(ready),formalNamedActual=14,formalSamples=2000,sourceModelSHA256=sha(B/'input_block.qnt'),
    reviewed='Complete contract/model and actual14-name proof; owning Monocle active-target callback/recalculate/clear, CWindow acceptsInput, actual tiledLayout typeid getter and workspace rule interface; source/raw causal audit.',
    approved='Fresh source-only B11 monocle and independent B12 component collector, preserving whole failed Bv4 ancestry/raw/audits/formal corrections. Exact current algorithm/owner+peer/source/native-mode/group/input/focus scope must be observed before physical input. Source-bound CPU refusal and complete inverse proof before root freeze/GUI grant.',
    constraints=['No allows_input denial assumption or private-field writes; no observer rebuild needed for actual layout getter.',
        'Retain mapped/unhidden/noFocusFalse/acceptsInputFalse, real balanced pointer/unchanged owner callback/core+Seat non-revival and original4s bound.',
        'Observe actual clear before owner unpin; numeric reason and rendered visibility are not directly proved by algorithm attestation.',
        'B12 only earns its actual component; no full12 or fullB claim until required combined acceptance.',
        'All original first10 methods and19 inherited tests remain byte-exact; preserve helpers/pair/root-normal-lifecycle checks.'],
    sourceImplementationAuthorized=True,GUIAuthorized=False,nativeAccepted=False,mainChanged=False)
raw=(json.dumps(row,indent=2)+'\n').encode()
with os.fdopen(os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
print(json.dumps(dict(result='pass',grantSHA256=sha(out),actualNamed=14,GUIAuthorized=False)))
