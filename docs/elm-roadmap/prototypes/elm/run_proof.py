"""Run only through protected QA; CPU Elm compiler/reducer learning proof."""
import hashlib,json,subprocess,datetime
from pathlib import Path
root=Path(__file__).resolve().parent
commands=[['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','--version'],['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm','--output=main.js'],['node','run.cjs']]
entries=[]
for n,command in enumerate(commands):
 p=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=180)
 (root/f'execution-{n}.stdout').write_text(p.stdout);(root/f'execution-{n}.stderr').write_text(p.stderr)
 entries.append(dict(command=command,exitCode=p.returncode,stdout=f'execution-{n}.stdout',stderr=f'execution-{n}.stderr'))
 if p.returncode:break
passed=len(entries)==3 and all(x['exitCode']==0 for x in entries)
if passed:
 results=json.loads((root/'results.json').read_text());passed=len(results['results'])==8 and all(x['passed'] for x in results['results'])
files=['src/Main.elm','elm.json','run.cjs','main.js','results.json','run_proof.py']+[f'execution-{n}.{kind}' for n in range(len(entries)) for kind in ['stdout','stderr']]
manifest=dict(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Headless compiled Elm reducer only; no host, subscriptions, native effects or GPU qualification',commands=entries,passed=passed,files=[dict(path=f,sha256=hashlib.sha256((root/f).read_bytes()).hexdigest()) for f in files if (root/f).exists()])
(root/'proof-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(passed=passed,tests=8 if passed else 0)));raise SystemExit(not passed)
