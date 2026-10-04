"""Serial dispatcher only; each reviewed native child uses the shared coordinator."""
import hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
cases=['elm-keyboard-focus-regressions-v157/parent-loss', 'elm-keyboard-focus-regressions-v157/mask-1', 'elm-keyboard-focus-regressions-v157/mask-2', 'elm-keyboard-focus-regressions-v157/mask-3', 'elm-keyboard-focus-regressions-v157/input', 'elm-keyboard-focus-regressions-v157/geometry', 'elm-keyboard-focus-regressions-v157/unheld', 'elm-keyboard-focus-regressions-v157/pointer']
out=ROOT/('dispatch-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'scope':'Serial reviewed native dispatch; individual report/cleanup/ABI evidence required','cases':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
code=0
for name in cases:
 root=REPO/'implementation'/name;runner=root/'qa/native.py';before=set((root/'qa').glob('native-*/report.json'))
 accepted=[p for p in before if json.loads(p.read_text()).get('passed') is True]
 if accepted:
  assert len(accepted)==1;path=accepted[0];r=json.loads(path.read_text());assert r['cleanupPassed']
  report['cases'].append({'root':str(root),'alreadyCompleted':True,'report':str(path),'reportSHA256':sha(path)});continue
 cmd=['/usr/bin/python3','-B',str(REPO/'implementation/elm-build-loop-v1/loop.py'),'native','--runner',str(runner)]
 p=subprocess.run(cmd,cwd=REPO,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True)
 label=name.replace('/','--');(out/(label+'.stdout')).write_bytes(p.stdout);(out/(label+'.stderr')).write_bytes(p.stderr)
 new=set((root/'qa').glob('native-*/report.json'))-before
 row={'root':str(root),'runnerSHA256':sha(runner),'command':cmd,'exitCode':p.returncode,'reports':[{'path':str(v),'sha256':sha(v)} for v in sorted(new)]}
 report['cases'].append(row);print(json.dumps(row),flush=True)
 if p.returncode!=0:code=p.returncode;break
 assert len(new)==1;r=json.loads(next(iter(new)).read_text());assert r['passed'] and r['cleanupPassed']
report['passed']=code==0 and len(report['cases'])==len(cases)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json',flush=True)
raise SystemExit(code if code else int(not report['passed']))
