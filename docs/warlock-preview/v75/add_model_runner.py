"""Derive explicitly selected coupled resume runner without inherited claims."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v67')
text=(r/'qa/enrollment-check.py').read_text().replace('enrollment','resume').replace("('resume-check-'","('resume-model-check-'")
start=text.index("'projection':");end=text.index(",'fixedFixture'",start)
text=text[:start]+"'projection':'Actual retained resume helper, original receiver mutex guard, native Broker reservation/proof/floor and intent cutoff; synthetic native clock/scope, no real capture or whole ImportedClients refinement'"+text[end:]
start=text.index("'fixedFixture':");end=text.index(",'toolSHA256'",start)
text=text[:start]+"'fixedFixture':{'binding':[1,2,3],'incarnations':[11,12,13],'clock':10,'nativeNow':4,'resumeCutoff':2000000004,'oldJobDeadline':100,'items':2,'bytes':64}"+text[end:]
start=text.index(" original={name:");end=text.index(" report['mutants']",start)
text=text[:start]+''' mutants=[('native/imported_lifecycle.hpp','expired-resume','if(intent->deadline<=s.now)return {ImportedIntentLedger::Admission::Expired,{},"[]"};','if(false)return {ImportedIntentLedger::Admission::Expired,{},"[]"};','expiryAfterCapacityReturn'),('native/imported_enrollment.hpp','reused-receiver','return view && epoch && view->epoch==epoch && view->binding==owner;','return view && epoch && view->binding==owner;','replacedReceiverBeforeQuery'),('qa/resume-checks.cpp','unknown-rejection','known=result.native.job.has_value();','known=result.native.status==demand::Attempt::Status::Started;','actualIssuedRejectionKnown')];caught=[]
 for filename,name,old,new,witness in mutants:
  original=(OUT/'inputs'/filename).read_text();assert original.count(old)==1
  mutant=OUT/name;shutil.copytree(OUT/'inputs',mutant);(mutant/filename).write_text(original.replace(old,new,1))
  run(name+'-compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-I'+str(mutant/'native'),str(mutant/'qa/resume-checks.cpp'),str(mutant/'native/preview_uri.cpp'),'-o',str(mutant/'checks'),*flags])
  matches=[key for key in traceInputs if witness in key];assert len(matches)==1;stdin,wanted=traceInputs[matches[0]]
  p=subprocess.run([str(mutant/'checks')],capture_output=True,text=True,input=stdin,timeout=30)
  (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
  actual=[json.loads(line) for line in p.stdout.splitlines()];assert p.returncode!=0 or actual!=wanted,(name,'unsafe mutant escaped actual trace oracle');caught.append({'name':name,'trace':matches[0],'differentObservableState':True,'exitCode':p.returncode})
''' + text[end:]
# Successful trace generators retain source/model file integrity and use eight
# actual named scenarios plus sixteen sampled traces, as the inherited runner.
target=r/'qa/resume-model-check.py';assert not target.exists();target.write_text(text);print(str(target))
