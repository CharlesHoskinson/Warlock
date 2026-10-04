"""Freeze native acknowledgement lineage and stronger protocol order audit."""
import hashlib,json,re,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path(__file__).resolve().parents[3]
ROOTS=[REPO/'implementation'/name for name in ['elm-surface-ack-v73','elm-surface-ack-qa-v74','elm-surface-ack-v75','elm-surface-ack-qa-v76','elm-surface-ack-v77','elm-surface-ack-qa-v78']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
root=ROOTS[4];build=root/'qa/build-1791081999173525186/report.json';checks=root/'qa/checks-1791082054917234030/report.json';model=root/'qa/model-1791082054916672609/report.json';native=ROOTS[5]/'qa/native-1791082037071505153/report.json'
for p in [build,checks]:
 d=json.loads(p.read_text());assert d['passed']
 for rel,h in d['inputs'].items():assert sha(root/rel)==h,rel
assert sha(build.parent/'elm-host')==json.loads(build.read_text())['binarySHA256']
assert json.loads(checks.read_text())['typedChecks']==31 and json.loads(checks.read_text())['presentationChecks']==12
m=json.loads(model.read_text());assert m['passed'] and m['namedScenarios']==9 and m['invariantSamples']==1000 and m['sourceSHA256']==sha(root/'spec/surfaces.qnt')
n=json.loads(native.read_text());assert n['passed'] and n['cleanupPassed'] and len(n['checks'])==36 and all(c['passed'] for c in n['checks'])
assert n['buildReportSHA256']==sha(build)
for path,h in n['inputs'].items():assert sha(Path(path))==h,path
lines=(native.parent/'native-evidence/elm-webview.log').read_text().splitlines();roles={};configured=[];opened=[];focus=[]
for i,line in enumerate(lines):
 role=re.search(r'xdg_surface[#@](\d+)\.get_popup\(new id xdg_popup[#@](\d+)',line)
 if role:roles[role[2]]=role[1]
 config=re.search(r'xdg_popup[#@](\d+)\.configure\((\d+), (\d+), (\d+), (\d+)\)',line)
 if config:
  assert tuple(map(int,config.groups()[1:]))==(50,48,700,420)
  configured.append((i,config[1],roles[config[1]]))
 if line.startswith('surface-popup-open:'):
  lease=re.search(r'lease=(\d+)',line)[1];c=next(c for c in reversed(configured) if c[0]<i)
  surface=c[2];j=next(j for j in range(c[0]+1,i) if re.search(r'xdg_surface[#@]'+surface+r'\.configure\((\d+)\)',lines[j]));serial=re.search(r'\.configure\((\d+)\)',lines[j])[1]
  k=next(k for k in range(j+1,i) if re.search(r'xdg_surface[#@]'+surface+r'\.ack_configure\('+serial+r'\)',lines[k]));opened.append({'lease':lease,'popupId':c[1],'surfaceId':surface,'configureLine':c[0],'surfaceConfigureLine':j,'ackLine':k,'openLine':i})
 if line.startswith('surface-focus-issued:'):
  pub,lease=re.search(r'publication=(\d+) lease=(\d+)',line).groups();o=next(o for o in reversed(opened) if o['lease']==lease and o['openLine']<i)
  applied=next(j for j in range(o['openLine']+1,i) if lines[j]=='surface-presentation-applied: publication='+pub+' lease='+lease)
  accepted=next(j for j in range(i+1,len(lines)) if lines[j]=='surface-focus-applied: publication='+pub+' lease='+lease)
  focus.append({**o,'publication':pub,'renderLine':applied,'focusIssueLine':i,'focusAppliedLine':accepted})
assert len(configured)==3 and len(focus)==3
assert 'backend-exit: waited=1 normal=1 code=0' in lines and 'host-exit: failure=0 rendered=1' in lines
(ROOTS[5]/'qa/protocol-focus-order.json').write_text(json.dumps({'passed':True,'sourceLogSHA256':sha(native.parent/'native-evidence/elm-webview.log'),'defaultConfigure':[50,48,700,420],'leases':focus,'scope':'Exact owning Wayland popup/surface configure and ack precede native grab completion, current DOM render and focus. No transformed/multi-output/hardware/AT acceptance.'},indent=2)+'\n')
for rejected in [ROOTS[1]/'qa/native-1791081591631022474/report.json',ROOTS[3]/'qa/native-1791081821283615934/report.json']:assert not json.loads(rejected.read_text())['passed']
source=json.loads((root/'research/source.json').read_text());assert source['sha256']==sha(root/'research/xdg-popup-surface.c')
for r in ROOTS:
 inventory={str(p.relative_to(r)):sha(p) for p in sorted(r.rglob('*')) if p.is_file() and 'elm-stuff' not in p.parts and p.name!='slice-manifest.json'}
 accepted=r in ROOTS[4:]
 result={'sourceClosurePassed':True,'nativeCandidateAccepted':accepted,'wholeFeatureAccepted':False,'completedRequirementIds':[],'acceptedCandidate':'implementation/elm-surface-ack-v77','acceptedNativeEvidence':str(native.relative_to(REPO)),'compiledChecks':[31,12],'hostCTestGroups':6,'surfaceCTestGroups':4,'quintNamedRuns':9,'quintInvariantSamples':1000,'nativeChecks':36,'scope':'Bounded V77/V78 default role/input/render/focus/owned launch acceptance only; V73/V74 and V75/V76 rejected routes preserved','files':inventory}
 (r/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(r/'qa/slice-manifest.json')
