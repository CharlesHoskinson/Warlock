"""Apply frozen compiled V21 decoder to actual V23 native packets."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ANCESTOR=ROOT.parent/'elm-trace-validation-v21';m=json.loads((ANCESTOR/'qa/slice-manifest.json').read_text());assert m['passed']
for rel,digest in m['files'].items():assert sha(ANCESTOR/rel)==digest,rel
compiled=ANCESTOR/'qa/elm-1791066419735708642/replay.js'
natives=[ROOT.parent/'elm-output-mapping-v25/qa/native-1791067430470077279/report.json',ROOT/'qa/native-1791067554195341385/report.json']
OUT=ROOT/'qa'/('trace-'+str(time.time_ns()));OUT.mkdir()
for path in [compiled,ROOT/'qa/trace.cjs',Path(__file__)]:shutil.copy2(path,OUT/path.name)
inputs={str(path):sha(path) for path in [compiled,ROOT/'qa/trace.cjs',Path(__file__),*natives]}
command=['node',str(OUT/'replay.js'),str(OUT/'checks.json'),*[str(p) for p in natives]]
command.insert(1,str(OUT/'trace.cjs'))
p=subprocess.run(command,capture_output=True,text=True,timeout=30)
(OUT/'stdout').write_text(p.stdout);(OUT/'stderr').write_text(p.stderr)
checks=json.loads((OUT/'checks.json').read_text()) if (OUT/'checks.json').exists() else {}
passed=p.returncode==0 and checks.get('passed') and checks.get('checks')==109 and all(sha(path)==digest for path,digest in inputs.items())
report={'passed':bool(passed),'scope':'Historical compiled decoder against109 actual output/mask native packets; no additional compiler or model run','inputs':inputs,'command':command,'exitCode':p.returncode,'checks':checks.get('checks'),'checksSHA256':sha(OUT/'checks.json') if checks else None,'ancestorManifestSHA256':sha(ANCESTOR/'qa/slice-manifest.json')}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not passed)
