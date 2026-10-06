"""Create native113 from held109 with reviewed phase and final GUI76 dependency."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');source=r/'docs/warlock-preview/v77/prepare_native110.py';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
partial=r/'implementation/warlock-client-provider-native-v112';m=partial/'PREPARATION-HELD.json';assert not m.exists()
m.write_text(json.dumps({'sourceHeld':True,'nativeLaunched':False,'purpose':'Unrun reviewed GUI75 preparation retained; final native113 will depend on currentGUI76 fixture qualification. No source/native campaign failure.','inputs':{str(p.relative_to(partial)):sha(p) for p in sorted(partial.rglob('*')) if p.is_file()}},indent=2)+'\n')
s=source.read_text();old="t=r/'implementation/warlock-client-provider-native-v110'";assert s.count(old)==1;s=s.replace(old,"t=r/'implementation/warlock-client-provider-native-v113'")
old='f=t/\'qa/native.py\';s=f.read_text();marker="   writeControl(growthControl,\'2 quit\');";assert s.count(marker)==1';assert s.count(old)==1;s=s.replace(old,old[:-1]+'2')
old="s=s.replace(marker,addition+marker);f.write_text(s)\n(t/'ANCESTRY.json')";assert s.count(old)==1;s=s.replace(old,"s=s.replace(marker,addition+marker,1);ast.parse(s);f.write_text(s)\n(t/'ANCESTRY.json')")
s=s.replace('implementation/warlock-preview-provider-v74','implementation/warlock-preview-provider-v76');ast.parse(s)
exec(compile(s,str(source),'exec'),{'__name__':'__main__','__file__':str(source),'ast':ast})
