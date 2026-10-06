"""Use reviewed model files with actual unchanged68 native production."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v68';review=r/'docs/warlock-preview/v75/model-review'
s=(p/'qa/resume-model-check.py').read_text().replace("ROOT=pathlib.Path(__file__).resolve().parents[1]","ROOT=pathlib.Path("+repr(str(p))+")")
s=s.replace("OUT=ROOT/'qa'/('resume-model-check-'+str(time.time_ns()))","OUT=pathlib.Path("+repr(str(review))+ ")/('coupled-'+str(time.time_ns()))")
s=s.replace("for rel in ['spec/resume.qnt','spec/resume_tests.qnt','qa/resume-model-check.py','qa/resume-checks.cpp']:inputs[rel]=sha(ROOT/rel)","for rel in ['spec/resume.qnt','spec/resume_tests.qnt','qa/resume-model-check.py','qa/resume-checks.cpp']:inputs[rel]=sha((pathlib.Path("+repr(str(review))+")/pathlib.Path(rel).name) if rel.startswith('spec/') else ROOT/rel)")
s=s.replace("shutil.copy2(ROOT/rel,target)","shutil.copy2((pathlib.Path("+repr(str(review))+")/pathlib.Path(rel).name) if rel.startswith('spec/') else ROOT/rel,target)")
s=s.replace("all(sha(ROOT/rel)==h for rel,h in inputs.items())","all(sha((pathlib.Path("+repr(str(review))+")/pathlib.Path(rel).name) if rel.startswith('spec/') else ROOT/rel)==h for rel,h in inputs.items())")
target=review/'coupled-runner.py';assert not target.exists();target.write_text(s)
exec(compile(s,str(target),'exec'),{'__file__':str(target),'__name__':'__main__'})
