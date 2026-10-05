"""Structural documentation validation; never certifies native release acceptance."""
import datetime,hashlib,json,os,pathlib,re,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[3]
OUT=ROOT/'qa'/('validation-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));OUT.mkdir()
checks=[]
def check(name,ok):
 checks.append({'name':name,'passed':bool(ok)})
 assert ok,name
def read(name):return json.loads((ROOT/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
try:
 manifest=read('source-manifest.json')
 check('338 frozen inputs byte-identical',len(manifest['files'])==338 and all(sha(ROOT/'inputs'/rel)==row['sha256'] for rel,row in manifest['files'].items()))
 for rel in ['docs/elm-roadmap/requirements.json','docs/elm-roadmap/delivery/sprint-backlog.json','docs/elm-roadmap/RIGHT-CLICK.md']:
  check('authoritative input unchanged '+rel,sha(REPO/rel)==manifest['files'][rel]['sha256'])
 ballot=read('candidates-v3.json');reqs=ballot['requirements'];remaining=read('remaining-work-v2.json');closure=remaining['closureRequirements']
 check('30 unique adoption IDs and67 scenarios',len(reqs)==30 and len({r['id'] for r in reqs})==30 and sum(len(r['scenarios']) for r in reqs)==67)
 check('53 proposals accounted',len(ballot['proposalDispositions'])==53)
 check('ten initial reports hash-bound',len(ballot['reports'])==10 and all(sha(ROOT/r['path'])==r['sha256'] for r in ballot['reports'].values()))
 base=read('inputs/docs/elm-roadmap/requirements.json')['requirements'];coverage=remaining['coverage'];byid={r['id']:r for r in base}
 check('242 baseline requirements/417 scenarios preserved',len(coverage)==242 and sum(len(r['originalScenarios']) for r in coverage)==417 and all(r['originalEARS']==byid[r['baselineId']]['ears'] and r['originalScenarios']==byid[r['baselineId']]['scenarios'] for r in coverage))
 check('baseline mapped once',len({r['baselineId'] for r in coverage})==242)
 check('24 closure contracts/48 scenarios',len(closure)==24 and sum(len(r['scenarios']) for r in closure)==48)
 check('right-click amendment remains separate24/48',remaining['amendmentCounts']['requirements']==24 and remaining['amendmentCounts']['scenarios']==48 and remaining['amendmentCounts']['separateFromBaseline'])
 old=read('inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.json')
 check('all12 prior workitems and44 findings crosswalked',len(remaining['frpWorkItemCrosswalk'])==12 and len(remaining['frpFindingCrosswalk'])==44 and {r['findingId'] for r in remaining['frpFindingCrosswalk']}=={r['id'] for r in old['findings']} and all(r['packages'] for r in remaining['frpFindingCrosswalk']))
 registry=read('requirements.json')
 check('canonical adoption preserves exact contracts',len(registry['requirements'])==30 and all(x['ears']==y['ears'] and x['scenarios']==y['scenarios'] for x,y in zip(registry['requirements'],reqs)))
 check('all30 adoption drafts package mapped',len(remaining['adoptionPackageCrosswalk'])==30)

 for change,rows in [('elm-design-adoption',reqs),('elm-release-closure',closure)]:
  specs='\n'.join(p.read_text() for p in (REPO/'openspec/changes'/change/'specs').glob('*/spec.md')).replace('**GIVEN**','GIVEN').replace('**WHEN**','WHEN').replace('**THEN**','THEN')
  check(change+' exact EARS/scenario strings',all(r['ears'] in specs and all('#### Scenario: '+r['id']+' '+s['name'] in specs and '- GIVEN '+s['given'] in specs and '- WHEN '+s['when'] in specs and '- THEN '+s['then'] in specs for s in r['scenarios']) for r in rows))
  check(change+' EARS templates',all((change=='elm-release-closure' or len(r['ears'])<=500) and ' SHALL ' in r['ears'] and re.match(r'^(WHEN|WHILE|WHERE|IF|The)\b',r['ears']) for r in rows))
  tasks=(REPO/'openspec/changes'/change/'tasks.md').read_text();check(change+' implementation remains unchecked','[x]' not in tasks.lower() and '[ ]' in tasks)
  env=dict(os.environ,OPENSPEC_TELEMETRY='0',DO_NOT_TRACK='1',CI='true')
  result=subprocess.run(['/home/hoskinson/.local/share/mise/installs/node/latest/bin/npm','exec','--yes','--package=@fission-ai/openspec@1.14.0','--','openspec','validate',change,'--strict'],cwd=REPO,env=env,text=True,capture_output=True,timeout=180)
  (OUT/(change+'.stdout')).write_text(result.stdout);(OUT/(change+'.stderr')).write_text(result.stderr);check(change+' OpenSpec1.14.0 strict',result.returncode==0)
 votes=[read('ratification/'+r['id']+'.votes.json') for r in read('request.json')['reviewers']]
 check('ten explicit exact-version ratifications',len(votes)==10 and all(v['ballotSHA256']==sha(ROOT/'candidates-v2.json') and v['philosophySHA256']==sha(ROOT/'PHILOSOPHY-V2.md') and v['remainingWorkSHA256']==sha(ROOT/'remaining-work-v2.json') for v in votes))
 check('all29 core draft contracts accepted;015 deferred',all(len(v['votes'])==30 and {x['id'] for x in v['votes']}=={r['id'] for r in reqs} and all(x['decision'] in ['accept','refine'] if x['id']=='ELM-ADOPT-030' else (x['decision']=='accept' if x['id']!='ELM-ADOPT-015' else x['decision'] in ['accept','defer']) for x in v['votes']) and v['philosophy']['decision']=='accept' and v['remainingWork']['decision']=='accept' for v in votes))
 amendments=[read('amendment/'+r['id']+'.votes.json') for r in read('request.json')['reviewers']]
 check('ten exact one-scenario amendment endorsements',len(amendments)==10 and all(a['finalBallotSHA256']==sha(ROOT/'candidates-v3.json') and a['previousBallotSHA256']==sha(ROOT/'candidates-v2.json') and a['decision']=='accept' and a['carryForwardUnchangedVotes'] for a in amendments))
 amended=read('amendment/opus-execution.json');check('five actual Opus amendment executions passed',amended['allTerminal'] and all(r['passed'] for r in amended['reviewers']))
 execution=read('ratification/opus-execution.json');check('five actual Opus5.5 executions passed',execution['allTerminal'] and len(execution['reviewers'])==5 and all(r['passed'] and r['exitCode']==0 and r['modelObserved']=='claude-opus-5-5' for r in execution['reviewers']))
 check('canonical philosophy exact',sha(ROOT/'PHILOSOPHY.md')==sha(ROOT/'PHILOSOPHY-V2.md'))
 status='PASS'
except Exception as exc:
 status='FAIL';checks.append({'error':repr(exc),'passed':False})
report={'status':status,'scope':scope,'checks':checks,'nativeAcceptance':False,'fullReleaseComplete':False}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':status,'checks':len(checks),'report':str(OUT/'report.json')}));sys.exit(status!='PASS')
