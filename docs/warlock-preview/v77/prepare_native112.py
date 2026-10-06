"""Precisely target the native insertion; retain failed111 preparation."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');source=r/'docs/warlock-preview/v77/prepare_native110.py';partial=r/'implementation/warlock-client-provider-native-v111';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
failure=partial/'PREPARATION-FAILURE.json';assert not failure.exists()
failure.write_text(json.dumps({'passed':False,'nativeLaunched':False,'failure':'Wrapper111 replaced both marker-count assertions; preflight marker remains unique and correctly refused. New112 modifies only the exact native-phase marker assertion and inserts only at the first reviewed occurrence. No native campaign has launched.','inputs':{str(p.relative_to(partial)):sha(p) for p in sorted(partial.rglob('*')) if p.is_file()}},indent=2)+'\n')
s=source.read_text();old="t=r/'implementation/warlock-client-provider-native-v110'";assert s.count(old)==1;s=s.replace(old,"t=r/'implementation/warlock-client-provider-native-v112'")
old='f=t/\'qa/native.py\';s=f.read_text();marker="   writeControl(growthControl,\'2 quit\');";assert s.count(marker)==1';assert s.count(old)==1;s=s.replace(old,old[:-1]+'2')
old="s=s.replace(marker,addition+marker);f.write_text(s)\n(t/'ANCESTRY.json')";assert s.count(old)==1;s=s.replace(old,"s=s.replace(marker,addition+marker,1);ast.parse(s);f.write_text(s)\n(t/'ANCESTRY.json')")
s=s.replace("implementation/warlock-preview-provider-v74","implementation/warlock-preview-provider-v75")
ast.parse(s);exec(compile(s,str(source),'exec'),{'__name__':'__main__','__file__':str(source),'ast':ast})
