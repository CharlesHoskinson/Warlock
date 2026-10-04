from pathlib import Path
import hashlib,json,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parents[1];repo=root.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
registry=repo/'docs/elm-roadmap/requirements.json';backlog=repo/'docs/elm-roadmap/delivery/sprint-backlog.json'
canonical={r['id']:r for r in json.loads(registry.read_text())['requirements']};tasks={r['id']:r for r in json.loads(backlog.read_text())['backlog']}
mapping=json.loads((root/'scenario-map.json').read_text());assert sha(registry)==mapping['registrySHA256'];assert sha(backlog)==mapping['backlogSHA256']
seen=set();scenario_count=0
for row in mapping['requirements']:
 identity=row['requirementId'];assert identity not in seen;seen.add(identity);r=canonical[identity];task=tasks[identity]
 assert row['ears']==r['ears'] and row['verification']==r['verification']
 assert row['sprint']==task['sprint'] and row['taskId']==task['taskId']
 assert len(row['scenarios'])==len(r['scenarios'])
 for actual,expected in zip(row['scenarios'],r['scenarios']):
  assert actual=={'id':identity+' '+expected['name'],**expected,'acceptedByThisPlan':False}
  assert actual['id'] in task['acceptanceScenarioIds'];scenario_count+=1
sources=[registry,backlog,*[repo/'docs/elm-roadmap'/name for name in ['SPRINTS.md','REQUIREMENTS.md','ARCHITECTURE.md','LAYERING.md','UI-UX-TEST-STRATEGY.md','RIGHT-CLICK.md','delivery/budgets.json']],repo/'implementation/elm-core-xdg-origin-projection-v470/component-manifest.json',repo/'implementation/elm-xdg-origin-owning-pair-v471/native-build-report.json',repo/'implementation/elm-xdg-pointer-current-tuple-v229/component-manifest.json',repo/'implementation/elm-xdg-pointer-current-acceptance-v231/component-manifest.json',repo/'implementation/elm-xdg-pointer-current-acceptance-v231/HANDOFF.md',repo/'implementation/elm-xdg-origin-combined-qualification-v484/HANDOFF.md',repo/'implementation/elm-input-region-fix-v23/birth_fixture.py',repo/'implementation/elm-input-region-fix-v23/qa/lifecycle_native.py',Path('/usr/include/gtk-4.0/gdk/wayland/gdkwaylandsurface.h'),Path('/usr/include/gtk-3.0/gdk/wayland/gdkwaylandwindow.h')]
external={str(p):{'sha256':sha(p),'size':p.stat().st_size} for p in sources}
files={str(p.relative_to(root)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(root.rglob('*')) if p.is_file() and p.name not in ('component-manifest.json','verification.json')}
report={'passed':True,'scope':'Requirements/scenario source-plan exactness only; no compile/native/acceptance','requirements':len(seen),'scenarios':scenario_count,'sourcePins':len(external),'nativeAccepted':False}
(root/'verification.json').write_text(json.dumps(report,indent=2)+'\n');files['verification.json']={'sha256':sha(root/'verification.json'),'size':(root/'verification.json').stat().st_size}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':report['scope'],'nativeAccepted':False,'files':files,'externalFiles':external}
out=root/'component-manifest.json';assert not out.exists();out.write_text(json.dumps(packet,indent=2)+'\n')
for name,row in files.items():assert sha(root/name)==row['sha256']
for name,row in external.items():assert sha(name)==row['sha256']
print(json.dumps({**report,'manifestSHA256':sha(out)}))
