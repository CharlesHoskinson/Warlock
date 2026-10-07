"""Create one bounded, shared evidence packet for nine critical workflow audits."""
import datetime,hashlib,json,pathlib,shutil,subprocess
R=pathlib.Path('/home/hoskinson/omarchy-windows-parity');O=pathlib.Path(__file__).parent;I=O/'inputs';I.mkdir(exist_ok=False)
now=datetime.datetime.now(datetime.timezone.utc);start=now-datetime.timedelta(hours=24)
def git(*args):return subprocess.check_output(['git','--no-pager',*args],cwd=R,text=True)
def put(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
rows=[]
for line in git('log','--since='+start.isoformat(),'--reverse','--format=%H%x09%cI%x09%s').splitlines():
 h,t,title=line.split('\t',2);counts={'productSourceFiles':0,'qaFiles':0,'documentationFiles':0,'otherFiles':0};production=[]
 for path in git('diff-tree','--no-commit-id','--name-only','-r',h).splitlines():
  if path.startswith('implementation/') and '/qa/' not in path and '/build-' not in path and '/inputs/' not in path and any('/'+d+'/' in path for d in ['src','native','adapter','assets']):counts['productSourceFiles']+=1;production.append(path)
  elif '/qa/' in path or '/build-' in path or '/inputs/' in path:counts['qaFiles']+=1
  elif path.startswith(('docs/','openspec/','DesignLanguage/')):counts['documentationFiles']+=1
  else:counts['otherFiles']+=1
 rows.append({'commit':h,'committedUTC':t,'title':title,'pathCounts':counts,'productPaths':production})
put(I/'git-24h.json',json.dumps({'startUTC':start.isoformat(),'endUTC':now.isoformat(),'head':git('rev-parse','HEAD').strip(),'commits':rows,'warning':'Path counts include repeated archival copies. They are NOT unique code changes, features or completed requirements.'},indent=2)+'\n')
files=['AGENTS.md','docs/HANDOFF.md','docs/warlock-build-loop/v1/INSTRUCTIONS.md','docs/elm-roadmap/BUILD-LOOP.md','docs/elm-roadmap/requirements.json','docs/elm-roadmap/delivery/implementation-status.json','docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.md','docs/elm-roadmap/research/20261005-design-adoption/WORKPLAN.md','docs/elm-roadmap/delivery/loop-state.json','DesignLanguage/WORKPLAN.md','docs/warlock-brand/PHILOSOPHY.md','docs/warlock-preview/v93/NATIVE-ADMISSION-CONTROLS.md','docs/warlock-preview/v93/OUTGOING-CONTROL-CONTRACT.md','docs/warlock-preview/v93/HANDOFF.md','docs/warlock-preview/v93/component-report-combined-restart-204-207.json','docs/warlock-preview/v93/component-report-gui143-shared-process-drain.json','docs/warlock-preview/v93/component-report-window-restart-198-201.json','openspec/changes/warlock-preview-actor-retirement/tasks.md','openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md']
for base in ['openspec/changes/elm-release-closure','openspec/changes/elm-desktop-pivot','openspec/changes/elm-design-adoption','openspec/changes/elm-right-click']:
 files += [str(p.relative_to(R)) for p in (R/base).rglob('*.md')]
gui=R/'implementation/warlock-preview-provider-v143'
files += [str(p.relative_to(R)) for p in (gui/'src').glob('*.elm') if p.name in {'Shell.elm','SurfaceController.elm','SurfaceRenderer.elm','TaskbarShell.elm','Taskbar.elm','Popup.elm','Bar.elm','Main.elm','Presentation.elm','Menu.elm','MenuBridge.elm','Catalog.elm','Inspection.elm'}]
files += [str(p.relative_to(R)) for p in (gui/'assets').glob('*') if p.name in {'shell.css','bar-adapter.js','popup-adapter.js','controlled-popup-adapter.js'}]
files += [str(p.relative_to(R)) for p in (gui/'native').glob('*') if p.name in {'controlled-preview-host.h','shared-host.c','preview-policy-driver.cpp','imported_clients.hpp','preview_client.hpp'}]
for rel in sorted(set(files)):
 p=R/rel
 if not p.is_file():continue
 target=I/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
deltas=[]
for v in range(94,144):
 root=R/f'implementation/warlock-preview-provider-v{v}'
 a=root/'ANCESTRY.json'
 if not a.exists():continue
 ancestry=json.loads(a.read_text());parent=pathlib.Path(ancestry.get('parent',''));changes=[]
 if not parent.is_dir():continue
 for base in ['src','native','adapter','assets']:
  for p in (root/base).glob('*'):
   if not p.is_file():continue
   q=parent/base/p.name
   if not q.exists() or p.read_bytes()!=q.read_bytes():
    import difflib
    delta=''.join(difflib.unified_diff(q.read_text(errors='replace').splitlines(True) if q.exists() else [],p.read_text(errors='replace').splitlines(True),fromfile=str(q.relative_to(R)),tofile=str(p.relative_to(R)),n=2))
    # Compiled JS is available in the repository; do not stuff duplicates into review contexts.
    if p.suffix=='.js' and p.stat().st_size>60000:delta='Generated JS delta omitted; inspect real source and build closure.\n'
    elif len(delta)>45000:delta=delta[:45000]+'\n[TRUNCATED: inspect original source path for full code]\n'
    changes.append({'path':str(p.relative_to(R)),'parent':str(q),'bytes':p.stat().st_size,'delta':delta})
 deltas.append({'version':v,'parent':str(parent),'purpose':ancestry.get('purpose',ancestry.get('change','')),'changes':changes})
put(I/'source-deltas-94-143.json',json.dumps(deltas,indent=2)+'\n')
brief='''# Critical after-action review: Warlock

User: "You have wasted a day and massive amounts of tokens." They request nine independent reviewers (3 Grok,3 Opus5.5,3 Astra), critical audit of workflow/productivity/development approach/velocity, a replacement workflow aimed at implementing remaining ORIGINAL EARS, its actual installation, and a rearmed completion goal. They return in about an hour. Do not defend the previous workflow or manufacture consensus.

Read this packet selectively; do not consume every archival duplicate. Start with original requirements.json, git-24h.json, old loop instructions, current implementation-status and current component reports. Then inspect source-deltas and actual GUI source for claims that require code. The full live repository is available READ ONLY at /home/hoskinson/omarchy-windows-parity; packets name exact source paths/commits so you can inspect any of the last24h work. No secrets/credential files, no desktop changes, no commands launching GUI/test campaigns, no edits to product. Review output is your only deliverable.

Audit the parent's claim that zero EARS were completed: implementation-status is an old integration lane and completedRequirementIds is empty; this is NOT proof that zero original requirements have existing valid evidence. Distinguish poor bookkeeping, partial implementation, actually satisfied original scenario, missing native acceptance, and entire-release acceptance. Do NOT require full release completion before any individual requirement can be closed. Do NOT relabel component or browser evidence native.

Last host goal snapshot before interruption: about7.9million tokens and22.5hours cumulative over the goal; no24h-only token telemetry is established. Source141/143 added genuine known renderer reload/failure drain. Latest two publications changed QA/supervisor/model/evidence, not production C/Elm behavior. Current controlled preview curtain is opacity0, root preview is ineligible, installed desktop unchanged; full release is unaccepted. Path/commit/test counts are not delivered value.

Expose fatal process flaws and the agent's own rationalizations. Propose a workflow that delivers original product behavior in a coherent application, with proportionate verification, cheap narrow reads, original scenario traceability and no fabricated authority. Preserve valid ABI/isolated-native-serialization/deadline/user-draft protections; propose ways to reduce archival duplication WITHOUT rewriting held evidence. Name specific safe first implementation task using existing original EARS IDs, code paths, target behavior and a small meaningful verification set. Also discuss how to close demonstrably completed original requirements rather than perpetually expanding internal CONTROL contracts.

Report <=1400 words: severity-ranked findings with concrete source citations; measured facts/uncertainties; stop/start/retain; proposed operating rules incl WIP, validation escalation, integration, reporting/cost controls; recommended first3 product slices with original IDs; risks and falsifiable success metrics. Be highly critical but evidence-based. No new agents, no broad research, no speculative additional gates. Recommend skills/plugins only if they remove a concrete delivery obstacle; reject irrelevant process overhead.
'''
put(O/'INDEX.md',brief)
roles={'grok_product':'Audit delivered user value, scope drift and prioritization; challenge choosing another cleanup primitive as the next task.','grok_velocity':'Audit productivity, token/compute waste, duplicated source/build/evidence and critical-path decisions; provide enforceable controls.','grok_workflow':'Audit the agent loop, evidence inflation and development method; propose a practical replacement with stop rules.','opus_architecture':'Audit genuine code progress versus prototype fragmentation, integration debt and immutable Elm policy use; propose a coherent integration path.','opus_requirements':'Audit original242 EARS/scenario traceability and zero-completed claim; select evidence-backed closures and implementation-first backlog.','opus_product':'Audit native UX, missing usable GUI, acceptance versus demo, and a product-focused release sequence.','astra_process':'Audit agent behavior and instructions causing endless QA; propose exact replacements, no-progress triggers, economics and reporting.','astra_code':'Audit actual24h source deltas and currentGUI; distinguish QA scaffolding from features and select first shippable code change.','astra_delivery':'Audit release critical path, existing potentially closed original EARS, safe integrated demos and a sustainable execution workflow.'}
for name,focus in roles.items():put(O/(name+'.prompt.txt'),f'You are independent critical reviewer {name}. Focus: {focus}\nRead {O}/INDEX.md and the shared inputs directory. Full repository read-only access is available. Be highly critical. Do not accept parent summaries without checking sources. Return <=1400 words, source-cited, specific and actionable. Never edit or spawn agents.\n')
manifest={str(p.relative_to(I)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in I.rglob('*') if p.is_file()}
put(O/'source-manifest.json',json.dumps({'schema':1,'snapshotUTC':now.isoformat(),'windowStartUTC':start.isoformat(),'repositoryHead':git('rev-parse','HEAD').strip(),'files':manifest},indent=2)+'\n')
put(O/'request.json',json.dumps({'schema':1,'models':{'grok':'grok-4.7','opus':'claude-opus-5-5','astra':'gpt-6-astra'},'reviewers':roles,'readOnly':True,'userRequests':'Critical nine-agent AAR then implementation-focused workflow installed and completion loop rearmed; full GUI scope retained.'},indent=2)+'\n')
print(json.dumps({'packet':str(O),'files':len(manifest),'commits24h':len(rows),'bytes':sum(x['bytes'] for x in manifest.values())}))
