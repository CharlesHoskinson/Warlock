"""Exact consensus and additive-spec verification under the protected CPU scope."""
import hashlib,json,pathlib,re,resource,subprocess,sys,time,os
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parent;R=ROOT/'research/v1'
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('contracts-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':scope,'checks':[],'nativeAcceptance':False,'fullReleaseAccepted':False}
def check(name,value):
 assert value,name
 report['checks'].append(name)
try:
 candidate=R/'candidate-v2.json';packet=json.loads(candidate.read_text());receipt=json.loads((R/'consensus-receipt-v2.json').read_text())
 check('exact candidate receipt',sha(candidate)==receipt['candidateSHA256'] and receipt['unanimous'] is True)
 ids={c['id'] for c in packet['contracts']};check('30 unique stable contracts',len(ids)==len(packet['contracts'])==30)
 original=[]
 for p in (R/'research').glob('*.proposals.json'):
  rows=json.loads(p.read_text());original.extend(rows if isinstance(rows,list) else rows['proposals'])
 check('all60 proposals routed',len(original)==60 and {r['id'] for r in original}=={i for c in packet['contracts'] for i in c['sourceProposals']})
 for name,prefix in [('source-manifest.json','inputs'),('supplemental-manifest.json','consensus-inputs')]:
  m=json.loads((R/name).read_text());check(name+' exact input bytes',all(sha(R/prefix/rel)==row['sha256'] for rel,row in m['files'].items()))
 for round in ['research','consensus','ratification-v2']:
  execution=json.loads((R/round/'opus-execution.json').read_text());check(round+' actual five terminal Opus/high executions',execution['allTerminal'] and len(execution['reviewers'])==5 and all(row['status']=='terminal' and row['exitCode']==0 and row['passed'] and row['modelObserved']=='claude-opus-5-5' and row['command'][row['command'].index('--effort')+1]=='high' for row in execution['reviewers']))
 for row in receipt['ballots']:
  p=REPO/row['path'];ballot=json.loads(p.read_text());check(row['reviewer']+' exact unanimous ballot',sha(p)==row['sha256'] and ballot['candidateSHA256']==sha(candidate) and len(ballot['votes'])==30 and {v['id'] for v in ballot['votes']}==ids and all(v['vote']=='accept' for v in ballot['votes']) and not ballot['blockingCorrections'])
 ears=(ROOT/'EARS.md').read_text();spec=(REPO/'openspec/changes/warlock-design-language/specs/warlock-design-language/spec.md').read_text()
 check('EARS exact voted requirements and guardrails',all(c['ears'] in ears and c['guardrail'] in ears for c in packet['contracts']))
 check('OpenSpec exact30 contracts and60 acceptance scenarios',len(re.findall(r'^### Requirement: WARLOCK-DL-',spec,re.M))==30 and len(re.findall(r'^#### Scenario: WARLOCK-DL-',spec,re.M))==60 and all(re.sub(r'\bshall\b','SHALL',c['ears']) in spec and c['guardrail'] in spec and all(a in spec for a in c['acceptance']) for c in packet['contracts']))
 cli=pathlib.Path('/home/hoskinson/.npm/_npx/b05ce0373733faa6/node_modules/@fission-ai/openspec/bin/openspec.js');before=sha(cli)
 p=subprocess.run(['node',str(cli),'validate','warlock-design-language','--strict','--json','--no-interactive'],cwd=REPO,env=dict(os.environ,OPENSPEC_TELEMETRY='0'),capture_output=True,text=True,timeout=60)
 (OUT/'openspec.stdout').write_text(p.stdout);(OUT/'openspec.stderr').write_text(p.stderr);check('OpenSpec1.14 strict validation',p.returncode==0 and sha(cli)==before)
 report['candidateSHA256']=sha(candidate);report['openspecCLI']={'path':str(cli),'sha256':before};report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error'),'report':str(OUT/'report.json')}));raise SystemExit(not report['passed'])
