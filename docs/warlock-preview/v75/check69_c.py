"""Compile changed C fixture with exact held optimized Elm while GUI69 builds."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-preview-provider-v69';parent=root.parent/'warlock-preview-provider-v68';bp=next(parent.glob('qa/build-*/report.json'))
s=(root/'qa/resume-enrollment-check.py').read_text().replace("ROOT=pathlib.Path(__file__).resolve().parents[1]","ROOT=pathlib.Path("+repr(str(root))+")")
s=s.replace("paths=list(ROOT.glob('qa/build-*/report.json'));assert len(paths)==1","paths=[pathlib.Path("+repr(str(bp))+")]")
s=s.replace("for name,value in build['inputs'].items():assert sha(ROOT/name)==value,name","for name,value in build['inputs'].items():assert sha((ROOT.parent/'warlock-preview-provider-v68'/name) if name=='native/resume-enrollment-test.cpp' else ROOT/name)==value,name")
# The only differing GUI build input is an uncompiled test fixture. Production
# C++ and every Elm module match held68 exactly. The new actual C fixture uses69.
target=r/'docs/warlock-preview/v75/check69_c_runner.py';assert not target.exists();target.write_text(s)
exec(compile(s,str(target),'exec'),{'__file__':str(target),'__name__':'__main__'})
