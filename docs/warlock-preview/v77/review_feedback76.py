"""Review typed cancellation proof in an owned scratch fixture before fresh76."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
p=pathlib.Path('/home/hoskinson/omarchy-windows-parity/docs/warlock-preview/v77/review_feedback75.py');s=p.read_text()
marker="report={'passed':False,";assert s.count(marker)==1
patch="f=out/'qa/feedback-replay.js';text=f.read_text();old=\"event:{kind:'refused',job:known}\";assert text.count(old)==1;text=text.replace(old,\"event:{kind:state(result).cancelling.length?'cancelled':'refused',job:known}\");f.write_text(text)\n"
s=s.replace(marker,patch+marker)
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
