"""Exact three-reviewer design parity, palette, contrast and OpenSpec checks."""
import hashlib,json,os,pathlib,re,resource,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('contracts-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'scope':scope,'nativeAcceptance':False,'fullReleaseAccepted':False,'checks':[],'contrasts':[]}
def check(name,value):assert value,name;r['checks'].append(name)
def luminance(color):
 values=[int(color[i:i+2],16)/255 for i in (1,3,5)];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values];return sum(v*w for v,w in zip(linear,[.2126,.7152,.0722]))
def contrast(a,b):
 values=sorted([luminance(a),luminance(b)]);return (values[1]+.05)/(values[0]+.05)
try:
 manifest=ROOT/'packet-manifest-v1.json';packet=json.loads(manifest.read_text());receipt=json.loads((ROOT/'consensus-receipt-v1.json').read_text());check('Exact packet receipt',sha(manifest)==receipt['packetSHA256'] and receipt['unanimous'] and receipt['reviewerCount']==3)
 for rel,digest in packet['files'].items():check('Packet '+rel,sha(REPO/rel)==digest)
 for rel,digest in json.loads((ROOT/'source-manifest.json').read_text())['files'].items():check('Frozen source '+rel,sha(REPO/rel)==digest)
 candidate=json.loads((ROOT/'candidate-v1.json').read_text());contracts=candidate['contracts'];ids={c['id'] for c in contracts};check('Fourteen unique requirements',len(ids)==len(contracts)==14);check('Thirty unique scenarios',len({s['id'] for c in contracts for s in c['scenarios']})==sum(len(c['scenarios']) for c in contracts)==30)
 for row in receipt['ballots']:
  path=REPO/row['path'];ballot=json.loads(path.read_text());check(row['role']+' exact acceptance',sha(path)==row['sha256'] and ballot['packetSHA256']==sha(manifest) and ballot['candidateSHA256']==sha(ROOT/'candidate-v1.json') and ballot['hashVerificationPassed'] and ballot['verdict']=='accept' and not ballot['blockingCorrections'] and len(ballot['votes'])==14 and {v['id'] for v in ballot['votes']}==ids and all(v['vote']=='accept' for v in ballot['votes']))
 ears=(ROOT/'EARS.md').read_text();spec=(REPO/'openspec/changes/warlock-layered-window-language/specs/warlock-layered-window-language/spec.md').read_text();check('EARS exact voted clauses',all(c['ears'] in ears for c in contracts));check('OpenSpec exact clauses/scenarios',len(re.findall(r'^### Requirement: WARLOCK-LAYER-',spec,re.M))==14 and len(re.findall(r'^#### Scenario: WARLOCK-LAYER-',spec,re.M))==30 and all(c['ears'] in spec and all(s['id'] in spec and s['given'] in spec and s['when'] in spec and s['then'] in spec for s in c['scenarios']) for c in contracts))
 tokens=json.loads((ROOT/'tokens.json').read_text());baseline=json.loads((REPO/tokens['extends']['path']).read_text());check('Palette preserved',tokens['reference']==baseline['reference'] and sha(REPO/tokens['extends']['path'])==tokens['extends']['sha256'])
 for theme,palette in tokens['reference'].items():
  for surface,bg in tokens['component']['chrome'][theme].items():
   for role,minRatio in [('text',4.5),('muted',4.5),('accent',3),('border',3)]:
    ratio=contrast(palette[role],bg);r['contrasts'].append({'theme':theme,'surface':surface,'role':role,'foreground':palette[role],'background':bg,'ratio':ratio,'minimum':minRatio});check(theme+' '+surface+' '+role+' opaque pair',ratio>=minRatio)
 check('Bounded effect recipes',tokens['component']['shadow']['maximumComponents']==2 and tokens['component']['shadow']['maximumBlur']==32 and all(len(v)<=2 and all(0<=s['blur']<=32 and s['spread']==0 for s in v) for v in tokens['component']['shadow']['roleRecipes'].values()) and tokens['component']['halo']['blur']==12 and tokens['component']['halo']['static'] and max(tokens['component']['familyBracket']['alpha'].values())<=.06 and not tokens['component']['familyBracket']['fullPerimeter'])
 check('No periodic decoration clock',tokens['component']['transition']['periodicDecorationTimers']==0 and tokens['component']['transition']['maximumMilliseconds']<=120 and tokens['component']['transition']['reducedMotionMilliseconds']==0 and tokens['component']['transition']['essentialBoundaryImmediate'])
 check('No false native qualification',not tokens['qualification']['nativeAcceptance'] and not receipt['nativeAcceptance'] and tokens['qualification']['numericCapsAreNotMeasuredS02Acceptance'])
 cli=pathlib.Path('/home/hoskinson/.npm/_npx/b05ce0373733faa6/node_modules/@fission-ai/openspec/bin/openspec.js');before=sha(cli);p=subprocess.run(['node',str(cli),'validate','warlock-layered-window-language','--strict','--json','--no-interactive'],cwd=REPO,env=dict(os.environ,OPENSPEC_TELEMETRY='0'),capture_output=True,text=True,timeout=60);(OUT/'openspec.stdout').write_text(p.stdout);(OUT/'openspec.stderr').write_text(p.stderr);check('Strict OpenSpec1.14',p.returncode==0 and sha(cli)==before)
 r.update(passed=True,packetSHA256=sha(manifest),candidateSHA256=sha(ROOT/'candidate-v1.json'),runnerSHA256=sha(pathlib.Path(__file__)),openspecCLI={'path':str(cli),'sha256':before})
except Exception as error:r['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'checks':len(r['checks']),'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
