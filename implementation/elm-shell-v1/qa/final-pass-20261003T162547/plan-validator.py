"""Structural EARS/OpenSpec/traceability validation, not native acceptance."""
import collections,datetime,hashlib,json,os,re,subprocess
from pathlib import Path
ROOT=Path('/home/hoskinson/omarchy-windows-parity/docs/elm-roadmap');REPO=ROOT.parents[1];CHANGE=REPO/'openspec/changes/elm-desktop-pivot'
reqs=json.loads((ROOT/'requirements.json').read_text())['requirements'];errors=[]
def check(condition,detail):
 if not condition:errors.append(detail)
check(len({r['id'] for r in reqs})==len(reqs),'duplicate requirement IDs')
patterns={'ubiquitous':r'^The .+ SHALL .+\.$','event-driven':r'^WHEN .+, (?:the|The) .+ SHALL .+\.$','state-driven':r'^WHILE .+, (?:the|The) .+ SHALL .+\.$','unwanted':r'^IF .+, THEN (?:the|The) .+ SHALL .+\.$','optional':r'^WHERE .+, (?:the|The) .+ SHALL .+\.$','complex':r'^(?:WHERE|WHILE) .+\b(?:WHEN|IF|WHILE) .+ SHALL .+\.$'}
tasks=(CHANGE/'tasks.md').read_text();taskRows=re.findall(r'^- \[ \] (P[0-8]-ELM-[A-Z]+-\d{3}):',tasks,re.M)
check(len(taskRows)==len(reqs),'implementation task multiplicity differs from requirement count')
check(len(taskRows)==len(set(taskRows)),'duplicate implementation task rows')
currentPhase=None
for line in tasks.splitlines():
 if line.startswith('## P'):currentPhase=line.split()[1]
 if line.startswith('- [ ] P'):check(line.split()[3].split('-')[0]==currentPhase,'task under incorrect phase heading: '+line[:70])
matrix=(ROOT/'TRACEABILITY.md').read_text();seenScenarios=[]
for r in reqs:
 check(len(r['ears'])<=500,r['id']+' normative statement exceeds 500 chars')
 check(bool(re.match(patterns[r['pattern']],r['ears'])),r['id']+' EARS pattern mismatch: '+r['ears'])
 check(r['phase'] in [f'P{i}' for i in range(9)],r['id']+' unknown phase')
 check(r['priority'] in ['must','conditional'],r['id']+' unknown priority')
 if r['phase'] in ['P7','P8']:check(r['priority']=='conditional',r['id']+' optional compositor marked mandatory')
 spec=(CHANGE/'specs'/r['capability']/'spec.md').read_text()
 check('\n'+r['ears']+'\n' in spec,r['id']+' divergent OpenSpec statement')
 check('### Requirement: '+r['id']+'\n' in spec,r['id']+' missing OpenSpec requirement')
 check('- [ ] '+r['taskId']+':' in tasks,r['id']+' missing/unexpectedly completed implementation task')
 check(r['id'] in matrix,r['id']+' missing traceability row')
 check(bool(r['verification'].strip()) and bool(r['task'].strip()) and bool(r['legacyEvidence'].strip()),r['id']+' missing verifier/task/evidence')
 check(bool(r['scenarios']),r['id']+' missing scenarios')
 check(bool(r.get('accountableOwnerRole')) and bool(r.get('verifierRole')) and r['accountableOwnerRole']!=r['verifierRole'],r['id']+' missing independent role mapping')
 scenarioNames={s['name'] for s in r['scenarios']}
 for obligation,names in r.get('scenarioObligations',{}).items():check(bool(names) and set(names)<=scenarioNames,r['id']+' obligation missing scenario: '+obligation)
 for s in r['scenarios']:
  key=r['id']+' '+s['name'];seenScenarios.append(key)
  check('#### Scenario: '+key+'\n' in spec,r['id']+' missing scenario')
  for field,marker in [('given','GIVEN'),('when','WHEN'),('then','THEN')]:
   check('- '+marker+' '+s[field]+'\n' in spec,r['id']+' divergent '+field+' scenario text')
  check(all(isinstance(s.get(k),str) and s[k].strip() for k in ['name','given','when','then']),r['id']+' malformed scenario')
check(len(set(seenScenarios))==len(seenScenarios),'duplicate scenario identifiers')
links=0
files=list(ROOT.glob('*.md'))+list((ROOT/'contributions').glob('*.md'))+list(CHANGE.glob('*.md'))+[ROOT/'reference/README.md']
for file in files:
 for link in re.findall(r'\]\(([^)]+)\)',file.read_text()):
  if '://' in link or link.startswith('#'):continue
  target=link.split('#')[0]
  check((file.parent/target).exists(),str(file.relative_to(REPO))+' broken link '+target);links+=1
# CLI is pinned; installing into npm cache is tooling only. No global/desktop install.
env=dict(os.environ,OPENSPEC_TELEMETRY='0',DO_NOT_TRACK='1',CI='true')
command=['npm','exec','--yes','--package=@fission-ai/openspec@1.14.0','--','openspec','validate','elm-desktop-pivot','--type','change','--strict','--json','--no-interactive']
try:
 p=subprocess.run(command,cwd=REPO,env=env,capture_output=True,text=True,timeout=180)
 cli={'command':command,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 check(p.returncode==0,'OpenSpec strict CLI validation failed')
except (OSError,subprocess.TimeoutExpired) as e:cli={'command':command,'error':str(e)};errors.append('OpenSpec CLI failed')
report={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Planning format, traceability and links; no implementation/native/GPU acceptance','requirements':len(reqs),'scenarios':len(seenScenarios),'capabilities':len({r['capability'] for r in reqs}),'localLinksChecked':links,'registrySHA256':hashlib.sha256((ROOT/'requirements.json').read_bytes()).hexdigest(),'errors':errors,'openspec':cli,'passed':not errors}
(Path('/home/hoskinson/omarchy-windows-parity/implementation/elm-shell-v1/qa/final-pass-20261003T162547/plan-validation.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));raise SystemExit(bool(errors))
