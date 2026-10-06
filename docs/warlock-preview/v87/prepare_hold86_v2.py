"""Retain generated freezer syntax failure; create reviewed corrected freezer."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/docs/warlock-preview/v87');old=r/'hold86.py'
s=old.read_text()
try:ast.parse(s);raise AssertionError('Expected preserved syntax failure')
except SyntaxError as e:(r/'hold86-preflight-failure.json').write_text(json.dumps({'passed':False,'source':str(old),'sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'error':str(e),'sourceMutated':False},indent=2)+'\n')
s=s.replace('],\\n    ','],\n    ');ast.parse(s);(r/'hold86-v2.py').write_text(s)
