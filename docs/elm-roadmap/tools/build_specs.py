"""Generate equivalent EARS/OpenSpec contracts from reviewed author inputs."""
import collections,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
CHANGE=REPO/'openspec/changes/elm-desktop-pivot'
inputs=sorted((ROOT/'contributions').glob('*.json'))+[ROOT/'coordinator-requirements.json']
reqs=[];normalizations=[]
for path in inputs:
 for item in json.loads(path.read_text()):
  r=dict(item)
  revisionsPath=ROOT/'revisions.json'
  if revisionsPath.exists():
   revision=json.loads(revisionsPath.read_text()).get('changes',{}).get(r['id'],{})
   r.update(revision)
  before=r['ears'];ears=before.strip()
  preamble,separator,response=ears.partition(' SHALL ')
  for word in ['when','while','where','if','then']:
   preamble=re.sub(r'\b'+word+r'\b',word.upper(),preamble,flags=re.I)
  ears=preamble+separator+response
  for subject in ['recovery tooling','activation tooling','supervision','native eligibility']:
   ears=ears.replace(', '+subject+' SHALL',', the '+subject+' SHALL')
   ears=ears.replace(', THEN '+subject+' SHALL',', THEN the '+subject+' SHALL')
  ears=ears.replace(', its native supervisor SHALL',', the native supervisor SHALL')
  if ears.startswith('IF ') and ' THEN ' not in ears:
   ears=re.sub(r',\s*(?=(?:the|The)\b)',', THEN ',ears,count=1)
  r['ears']=ears
  count=sum(bool(re.search(r'\b'+w+r'\b',ears.partition(' SHALL ')[0])) for w in ['WHEN','WHILE','WHERE','IF'])
  pattern='complex' if count>1 else {'WHEN':'event-driven','WHILE':'state-driven','WHERE':'optional','IF':'unwanted'}.get(ears.split()[0],'ubiquitous')
  if before!=ears or r['pattern']!=pattern:normalizations.append({'id':r['id'],'original':before,'normalized':ears,'originalPattern':r['pattern'],'pattern':pattern})
  r['pattern']=pattern;r['source']=str(path.relative_to(REPO));r['status']='proposed';r['taskId']=r['phase']+'-'+r['id']
  reqs.append(r)
ownerRoles={'elm-host':'Native host lead','elm-native-bridge':'Native authority lead','elm-taskbar':'Elm presentation lead','elm-switcher':'Elm policy lead','elm-shell-experience':'Desktop experience lead','elm-accessibility':'Accessibility lead','elm-capture-motion':'Graphics lead','elm-window-policy':'Native authority lead','elm-native-compositor':'Native compositor lead','elm-verification':'Verification lead','elm-performance':'Performance qualification lead','elm-delivery':'Release integration lead','elm-security':'Native security lead','elm-gpu':'Graphics lead','elm-layering':'Native authority lead'}
for r in reqs:
 r['accountableOwnerRole']=ownerRoles[r['capability']]
 r['verifierRole']='Independent acceptance reviewer'
reqs.sort(key=lambda r:r['id']);assert len({r['id'] for r in reqs})==len(reqs)
(ROOT/'requirements.json').write_text(json.dumps({'schema':1,'status':'proposed; implementation acceptance pending','requirements':reqs},indent=2)+'\n')
(ROOT/'normalizations.json').write_text(json.dumps(normalizations,indent=2)+'\n')
groups=collections.defaultdict(list)
for r in reqs:groups[r['capability']].append(r)
intro=['# EARS requirement inventory','','All statements below are proposed requirements for the Elm desktop and optional native compositor track. This file and the OpenSpec capability deltas are generated from [the canonical registry](requirements.json); identical normative text and stable IDs are retained. A requirement being listed does not mean it is implemented or accepted.','','Patterns use EARS: The/system/SHALL for ubiquitous behavior; WHEN for events; WHILE for states; IF/THEN for unwanted behavior; WHERE for selected features; combinations retain their clause order. [Originator guidance](https://alistairmavin.com/ears/).','','`must` requirements apply to the mandatory shell scope unless explicitly state-conditioned; `conditional` requirements apply only when the specified optional feature is selected. P7/P8 belong to the optional native compositor track. Every acceptance must execute its verification and retain evidence; existing CPU/native/model results are not interchangeable.','','[Traceability](TRACEABILITY.md) connects requirements, scenarios, tasks, phases and legacy/new proof obligations. [Author input normalizations](normalizations.json) record EARS keyword and pattern normalization; original inputs remain unchanged.','']
for capability,items in sorted(groups.items()):
 intro+=['## '+capability,'']
 lines=['# '+capability,'','## ADDED Requirements','']
 for r in items:
  intro+=['### '+r['id'],'',r['ears'],'',f"Pattern: {r['pattern']}. Phase: {r['phase']}. Priority: {r['priority']}. Status: proposed. Owner: {r['accountableOwnerRole']}; verifier: {r['verifierRole']}.",'','Verification: '+r['verification'],'','Evidence obligation: '+r['legacyEvidence'],'']
  lines+=['### Requirement: '+r['id'],'',r['ears'],'']
  for s in r['scenarios']:
   lines+=['#### Scenario: '+r['id']+' '+s['name'],'','- GIVEN '+s['given'],'- WHEN '+s['when'],'- THEN '+s['then'],'']
 dest=CHANGE/'specs'/capability/'spec.md';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text('\n'.join(lines)+'\n')
(ROOT/'REQUIREMENTS.md').write_text('\n'.join(intro)+'\n')
trace=['# Requirement traceability','','All acceptance is pending. Rows identify the planned verifier, not a test result. Scenarios are in proposed capability deltas; implementation tasks stay unchecked.','','| Requirement | Phase | Priority | OpenSpec requirement/scenarios | Task | Owner / verifier | Verification | Legacy/new evidence |','| --- | --- | --- | --- | --- | --- | --- | --- |']
def cell(s):return str(s).replace('|','\\|').replace('\n',' ')
for r in reqs:
 target=f"../../openspec/changes/elm-desktop-pivot/specs/{r['capability']}/spec.md#requirement-{r['id'].lower()}"
 trace.append('| '+' | '.join([r['id'],r['phase'],r['priority'],f"[{len(r['scenarios'])} scenario(s)]({target})",r['taskId'],cell(r['accountableOwnerRole']+' / '+r['verifierRole']),cell(r['verification']),cell(r['legacyEvidence'])])+' |')
(ROOT/'TRACEABILITY.md').write_text('\n'.join(trace)+'\n')
tasks=['# Implementation tasks','','Planning artifacts are drafted. Every implementation/qualification task remains unchecked. Phase dependencies and gates are in [the roadmap](../../../docs/elm-roadmap/ROADMAP.md). Optional P7/P8 tasks do not block mandatory shell delivery unless that replacement is selected.','','Completion requires each requirement’s specified verification and source-bound evidence, plus its phase-wide native acceptance gate.']
for phase in sorted({r['phase'] for r in reqs}):
 tasks+=['','## '+phase+(' — optional compositor' if phase in ['P7','P8'] else ''),'']
 for r in reqs:
  if r['phase']!=phase:continue
  tasks+=[f"- [ ] {r['taskId']}: {r['task']} Verify: {r['verification']}"]
(CHANGE/'tasks.md').write_text('\n'.join(tasks)+'\n')
if (ROOT/'revisions.json').exists():inputs.append(ROOT/'revisions.json')
summary={'requirements':len(reqs),'scenarios':sum(len(r['scenarios']) for r in reqs),'capabilities':len(groups),'phases':dict(collections.Counter(r['phase'] for r in reqs)),'inputs':[{'path':str(p.relative_to(REPO)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]}
(ROOT/'generation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='inputs'}))
