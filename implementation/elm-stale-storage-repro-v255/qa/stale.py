import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('stale-'+str(time.time_ns()));OUT.mkdir()
SOURCE=ROOT.parents[1]/'implementation/elm-storage-ux-v248'
build=next((SOURCE/'qa').glob('build-*/report.json'));assert json.loads(build.read_text())['passed']
p=subprocess.run(['node',str(ROOT/'qa/stale.cjs'),str(build.parent/'shell.js'),str(OUT/'replay.json')],capture_output=True,text=True,timeout=10)
(OUT/'stdout').write_text(p.stdout);(OUT/'stderr').write_text(p.stderr)
report={'passed':p.returncode==0,'exitCode':p.returncode,'inputs':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),ROOT/'qa/stale.cjs',SOURCE/'src/Shell.elm',build,build.parent/'shell.js']},'scope':'Compiled actual Elm failure/retry/Unknown presentation; native GUI proof separate'}
if p.returncode==0:report['checks']=json.loads((OUT/'replay.json').read_text())['checks']
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(p.returncode)
