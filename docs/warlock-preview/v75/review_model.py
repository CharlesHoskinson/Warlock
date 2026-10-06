"""Typecheck the next model correction before owning another GUI derivative."""
import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v68/spec';t=r/'docs/warlock-preview/v75/model-review';assert not t.exists();t.mkdir()
for name in ['resume.qnt','resume_tests.qnt']:(t/name).write_text((p/name).read_text().replace('val next=','val updated=').replace('...next,','...updated,'))
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
x=subprocess.run([tool,'typecheck','resume_tests.qnt'],cwd=t,capture_output=True,text=True,timeout=30);(t/'stdout').write_text(x.stdout);(t/'stderr').write_text(x.stderr);(t/'report.json').write_text(json.dumps({'passed':x.returncode==0,'exitCode':x.returncode,'scope':'Model-only reserved builtin identifier correction; no scenario/oracle/deadline/production changes'},indent=2)+'\n');print(x.stdout,x.stderr);sys.exit(x.returncode)
