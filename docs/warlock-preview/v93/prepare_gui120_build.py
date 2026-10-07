"""Link the native policy driver while retaining all original GUI119 commands."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v120')
s=(root/'qa/build-visual-channel.py').read_text()
for old,new in [
 ("'preview-visual-channel.cpp']","'preview-visual-channel.cpp','preview-policy-driver.cpp']"),
 ("str(OUT/'preview-visual-channel.cpp.o'),'-o'","str(OUT/'preview-visual-channel.cpp.o'),str(OUT/'preview-policy-driver.cpp.o'),'-o'"),
 ("'preview-visual-channel.cpp.d']","'preview-visual-channel.cpp.d','preview-policy-driver.cpp.d']")]:
 assert s.count(old)==1; s=s.replace(old,new)
ast.parse(s);p=root/'qa/build-policy-driver.py';assert not p.exists();p.write_text(s);print(p)
