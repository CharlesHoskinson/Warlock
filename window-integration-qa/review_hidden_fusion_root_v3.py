#!/usr/bin/python3
"""Review fused capture and align its final guard order with the checked model."""
import ast,datetime,hashlib,json,os,re,stat
from pathlib import Path
from qa_launch import require_qa_scope
scope=require_qa_scope();Q=Path('/home/hoskinson/window-integration-qa');B=Q/'hidden-capture-fusion-design-v2';O=Q/'hidden-capture-fusion-root-reviewed-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
H=B/'source-handoff.json';assert sha(H)=='b48d14140883f46e40b176f195c2e6ab02b5179956a75079250cf9386bf81cc9'
h=json.loads(H.read_bytes());assert h['inputCount']==202 and len(h['sources'])==202
for p,w in h['sources'].items():assert sha(p)==w['sha256'] and stat.S_IMODE(Path(p).stat().st_mode)==w['mode']
assert sha(h['patch']['path'])==h['patch']['sha256']=='ca3b961a3a88f3dba935d1ccbbaa33cc25e5441dab0c53e035777ef1db983720'
formal=json.loads((B/'formal-before-runtime.json').read_bytes())
assert formal['result']=='pass' and formal['namedActuallyRun']==23 and formal['samples']==2000 and formal['steps']==100
for x in formal['checks']:assert x['exitCode']==0 and sha(x['log'])==x['sha256']
named=next(x for x in formal['checks'] if 'test' in x['command'])
text=Path(named['log']).read_text();actual=re.findall(r'^\s*ok ([A-Za-z_][A-Za-z0-9_]*) passed \d+ test\(s\)',text,re.M)
assert len(actual)==23 and set(actual)==set(formal['names']) and '23 passing' in text
assert any('--match=' in a for a in named['command'])
assert h['retainedPixelMatrices']==16 and h['retainedExactPixelComparisons']==32 and h['pixelsNewlyRerun'] is False
assert h['fileAvailabilityCasesActuallyRun']==9 and h['runtimeApplied'] is False and h['ownedApplicationTestsExecuted'] is False
assert h['rootV6Actual45NamedCorrectionIncluded'] is True
proposed=(B/'native_desktop.py.proposed').read_text()
block="                    closed=True\n                    self.base.check_current(window)\n                    # Job closure does not prove both private files exist.\n                    if any(not path.is_file() or path.stat().st_size<64 for path in (temporary,composed)):\n                        raise ValueError('incomplete hidden pixel outputs')\n"
replacement="                    closed=True\n                    # Job closure does not prove both private files exist.\n                    if any(not path.is_file() or path.stat().st_size<64 for path in (temporary,composed)):\n                        raise ValueError('incomplete hidden pixel outputs')\n                    self.base.check_current(window)\n"
assert proposed.count(block)==1
corrected=proposed.replace(block,replacement,1)
assert corrected.replace(replacement,block,1)==proposed
ast.parse(corrected)
# Complete product inverse: only new private method and this one selection change.
start=corrected.index('    def _capture_hidden_fused(');end=corrected.index('    def _capture_source_impl(',start)
inverse=corrected[:start]+corrected[end:]
call="self._capture_hidden_fused(window,epoch) if type(self.commands) is OwnedCommands and type(self.preview_batch) is BatchPreviews else self.base.capture(window,epoch)"
assert inverse.count(call)==1
inverse=inverse.replace(call,'self.base.capture(window,epoch)',1)
parent=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-focus-transaction-v28')
assert inverse==(parent/'native_desktop.py').read_text()
def publish(p,raw):
    with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
O.mkdir(mode=0o700);source=O/'native_desktop.py.proposed';publish(source,corrected.encode())
row=dict(result='pass',schema='root-hidden-fusion-v3-application-grant',observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=scope,
    proposalHandoffSHA256=sha(H),proposalSources=202,correctedProposedSource=str(source),correctedProposedSourceSHA256=sha(source),rootReviewToolSHA256=sha(__file__),
    reviewed='Complete V2 patch/model, original hidden capture DAG/consumers/cleanup mapping, exact pixel evidence, explicit23-name/invariant proof and nine file availability cases.',
    finalGuardOrder='Normal owned closure, both private files present/nonempty, final current-native check, then original publication. This matches the already checked model; only one existing guard line moved.',
    wholeV28InverseExact=True,actualNamed=23,actualTraces=2000,retainedPixelComparisons=32,
    approved='Apply exact corrected single module to a fresh V29 derivative of frozen V28; preserve complete ancestors/raw failures/formal corrections; run meaningful actual OwnedCommands/Keeper capture/failure/legacy tests then required full CPU coverage. Return source-ready for root freeze and baseline38 review.',
    applicationAuthorized=True,GUIAuthorized=False,nativeAccepted=False,original38Accepted=False,original34Accepted=False,mainChanged=False)
out=Q/'hidden-capture-fusion-v3-root-application-grant-v1.json';publish(out,(json.dumps(row,indent=2)+'\n').encode())
print(json.dumps(dict(result='pass',grantSHA256=sha(out),proposedSourceSHA256=sha(source),proposalSources=202,GUIAuthorized=False)))
