"""Write exact proposed selector-only files and source conservation; no GUI/imports."""
import ast,difflib,hashlib,json,os,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa'); OLD=QA/'family-preparation-thumbnail-v9'; OUT=Path(__file__).resolve().parent
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-preview-lock-admission-v25')
MANIFEST=SERVICE/'manifest-preview-admission-v25.json'; EXPECTED='f0b6916151c587501ae73a8fcfacdcc5156c661289592358d13bce66e23ef6e2'
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(path,data):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
def dump(v):return (json.dumps(v,indent=2)+'\n').encode()
def main():
 assert sha(MANIFEST.read_bytes())==EXPECTED
 assert sha((OLD/'frozen-inputs.json').read_bytes())=='1820c23f20e585411a6245b23fb373b2119342ea441dce5dbcbb4000227b0444'
 changes={'module_binding.py':[
  ("SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')","SERVICE=Path('"+str(SERVICE)+"')"),
  ("MANIFEST=SERVICE/'manifest-family-preparation-v24.json'","MANIFEST=SERVICE/'manifest-preview-admission-v25.json'"),
  ("MANIFEST_SHA256='b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c'","MANIFEST_SHA256='"+EXPECTED+"'")],
  'native_faults.py':[("if SERVICE.name!='service-family-preparation-v24':","if SERVICE.name!='service-preview-lock-admission-v25':")]}
 patches=[];rows={}
 for name,replacements in changes.items():
  old=(OLD/name).read_text();new=old
  for before,after in replacements:
   assert new.count(before)==1,(name,before);new=new.replace(before,after)
  inverse=new
  for before,after in reversed(replacements):
   assert inverse.count(after)==1;inverse=inverse.replace(after,before)
  assert inverse==old
  ast.parse(new);save(OUT/(name+'.proposed'),new.encode())
  rows[name]={'originalSHA256':sha(old.encode()),'proposedSHA256':sha(new.encode()),'originalMode':stat.S_IMODE((OLD/name).stat().st_mode),'wholeFileInverseExact':True,'replacementCount':len(replacements)}
  patches+=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
 save(OUT/'intended-v10.patch',''.join(patches).encode())
 checked=['native_integration.py','native_faults.py','module_binding.py','service_observer.py','service_recovery_observer.py','recovery_observer.py','recovery_evidence.py','capture_evidence.py','verify_reversal.py','helper_observer.py','helper_setup.py','private_shell.py','test_actual_binding.py','test_batch_binding.py','test_renderer_collector_binding.py','renderer_binding_fixture.py','collector_v9_closure.py']
 functions={};whole={}
 for name in checked:
  raw=(OLD/name).read_bytes();tree=ast.parse(raw);whole[name]={'sha256':sha(raw),'mode':stat.S_IMODE((OLD/name).stat().st_mode)}
  for fn in tree.body:
   if isinstance(fn,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
    functions[name+':'+fn.name]=sha(ast.dump(fn,include_attributes=False).encode())
 baseline=ast.parse((OLD/'native_integration.py').read_bytes());fault=ast.parse((OLD/'native_faults.py').read_bytes());binding=ast.parse((OLD/'module_binding.py').read_bytes())
 original_main=next(x for x in baseline.body if isinstance(x,ast.FunctionDef)and x.name=='main')
 original_fault=next(x for x in fault.body if isinstance(x,ast.FunctionDef)and x.name=='main')
 proposed_fault=ast.parse((OUT/'native_faults.py.proposed').read_bytes());new_fault=next(x for x in proposed_fault.body if isinstance(x,ast.FunctionDef)and x.name=='main')
 for x in ast.walk(new_fault):
  if isinstance(x,ast.Constant)and x.value=='service-preview-lock-admission-v25':x.value='service-family-preparation-v24'
 assert ast.dump(new_fault,include_attributes=False)==ast.dump(original_fault,include_attributes=False)
 for field,n in [('MODULES',19),('LINKS',16)]:
  assignment=next(x for x in binding.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id==field for t in x.targets));assert len(ast.literal_eval(assignment.value))==n
 count=lambda node:sum(isinstance(x,ast.Call)and isinstance(x.func,ast.Name)and x.func.id=='check' for x in ast.walk(node))
 packet={'result':'pass','baseCollector':str(OLD),'selectedManifest':str(MANIFEST),'selectedManifestSHA256':EXPECTED,'changes':rows,'originalFiles':whole,'functionASTs':functions,'baselineMainByteExact':True,'faultMainSingleSelectorInverseExact':True,'moduleBindingEveryFunctionByteExact':True,'actualModules':19,'actualLinks':16,'baselineSyntacticCheckCalls':count(original_main),'faultSyntacticCheckCalls':count(original_fault),'requiredActualBaselineGates':38,'requiredActualFaultGates':34,'allOriginalDeadlinesExact':True,'allOriginalCallbacksArchiveQueryAndRefusalFunctionsExact':True,'nativeAccepted':False,'mainChanged':False}
 save(OUT/'source-conservation.json',dump(packet));save(OUT/'intended-source-map.json',dump(rows));print(json.dumps(packet))
if __name__=='__main__':main()
