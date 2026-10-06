"""Retain partial110 prep; insert new phase only at the reviewed first marker."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');old=r/'docs/warlock-preview/v77/prepare_native110.py';partial=r/'implementation/warlock-client-provider-native-v110';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
failure=partial/'PREPARATION-FAILURE.json';assert not failure.exists()
failure.write_text(json.dumps({'passed':False,'nativeLaunched':False,'failure':'Insertion marker also occurs in finally cleanup. Preparatory assertion correctly refused ambiguous replacement; no campaign launched. Fresh111 inserts once at the first reviewed marker, leaving original finally cleanup untouched.','inputs':{str(p.relative_to(partial)):sha(p) for p in sorted(partial.rglob('*')) if p.is_file()}},indent=2)+'\n')
s=old.read_text();s=s.replace("t=r/'implementation/warlock-client-provider-native-v110'","t=r/'implementation/warlock-client-provider-native-v111'")
s=s.replace('assert s.count(marker)==1\naddition=', 'assert s.count(marker)==2\naddition=')
s=s.replace('s=s.replace(marker,addition+marker);f.write_text(s)', 's=s.replace(marker,addition+marker,1);ast.parse(s);f.write_text(s)')
assert "t=r/'implementation/warlock-client-provider-native-v111'" in s and 'assert s.count(marker)==2' in s
exec(compile(s,str(old),'exec'),{'__name__':'__main__','__file__':str(old),'ast':ast})
