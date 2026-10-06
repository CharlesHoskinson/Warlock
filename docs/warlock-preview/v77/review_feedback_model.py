import json,pathlib,resource,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');source=r/'implementation/warlock-preview-provider-v74/spec'
out=r/'docs/warlock-preview/v77'/('model-review-'+str(time.time_ns()));out.mkdir()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
p=subprocess.run([tool,'typecheck','feedback_tests.qnt'],cwd=source,capture_output=True,text=True,timeout=180)
(out/'stdout').write_text(p.stdout);(out/'stderr').write_text(p.stderr);(out/'report.json').write_text(json.dumps({'passed':p.returncode==0,'exitCode':p.returncode,'scope':'Preliminary source typecheck only; selected implementation traces remain required.'},indent=2)+'\n');print(p.stdout+p.stderr);raise SystemExit(p.returncode)
