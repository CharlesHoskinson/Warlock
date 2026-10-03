"""Protected QA: requirement-to-sprint traceability and dependency validation."""
import datetime,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reqs=json.loads((root/'requirements.json').read_text())['requirements'];byid={x['id']:x for x in reqs}
p=json.loads((root/'delivery/sprint-backlog.json').read_text());slots={s['id']:s for s in p['sprints']}
assert p['requirementsSHA256']==sha(root/'requirements.json')
assert len(p['backlog'])==len(byid)==len({x['id'] for x in p['backlog']})
seen=[]
for s in p['sprints']:
 assert s['goal'] and s['deliverables'] and s['exitGate'] and s['durationWeeks']==2
 assert all(d in slots for d in s['dependsOn'])
 seen.extend(s['items'])
assert len(seen)==len(set(seen)) and set(seen)==set(byid)
for x in p['backlog']:
 r=byid[x['id']];s=slots[x['sprint']]
 assert x['id'] in s['items'] and x['phase']==r['phase']==s['phase']
 assert x['taskId']==r['taskId'] and x['status']=='backlog'
 assert x['ownerRole']==r['accountableOwnerRole'] and x['verifierRole']==r['verifierRole']
 assert x['acceptanceScenarioIds']==[r['id']+' '+n['name'] for n in r['scenarios']]
 assert s['track']==('conditional-compositor' if r['phase'] in ['P7','P8'] else 'mandatory-shell')
def visit(i,stack):
 assert i not in stack,'cyclic prerequisite: '+i
 for d in slots[i]['dependsOn']:visit(d,stack+[i])
for i in slots:visit(i,[])
assert p['capacity']['plannedMaximumEngineerWeeks']+p['capacity']['reservedEngineerWeeks']==p['capacity']['grossEngineerWeeks']
result=dict(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Sprint plan traceability, dependency and capacity arithmetic; not story estimates or implementation acceptance',requirements=len(byid),acceptanceScenarios=sum(len(x['acceptanceScenarioIds']) for x in p['backlog']),mandatorySlots=16,conditionalSlots=7,passed=True,files=[dict(path=str(f.relative_to(root)),sha256=sha(f)) for f in [root/'requirements.json',root/'SPRINTS.md',root/'ROADMAP.md',root/'delivery/sprint-backlog.json',Path(__file__),root/'tools/build_sprints.py']])
(root/'delivery/validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
