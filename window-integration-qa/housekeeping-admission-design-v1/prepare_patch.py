"""Intended source only; no candidate/controller edits."""
import ast,difflib,hashlib,json,os,stat
from pathlib import Path
D=Path(__file__).resolve().parent;B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-preview-lock-admission-v25')
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(p,b):
 with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def main():
 assert sha((B/'manifest-preview-admission-v25.json').read_bytes())=='f0b6916151c587501ae73a8fcfacdcc5156c661289592358d13bce66e23ef6e2'
 before="""        def clients():return json.loads(commands.check_output(['hyprctl','clients','-j'],env=self.guard.env,text=True,timeout=.6))
        before=clients()
        native=json.loads(commands.check_output(['hyprctl','repl','print(hl.plugin.hyprbars.window_families())'],env=self.guard.env,text=True,timeout=.6))
"""
 after="""        def query(arguments):
            with self.journal_lock:
                return json.loads(commands.check_output(arguments,env=self.guard.env,text=True,timeout=.6))
        def clients():return query(['hyprctl','clients','-j'])
        before=clients()
        native=query(['hyprctl','repl','print(hl.plugin.hyprbars.window_families())'])
"""
 fixture_before="        factory=NativeFactory.__new__(NativeFactory);factory.desktops=[];factory.shared_cache=cache\n";fixture_after=fixture_before+"        factory.journal_lock=__import__('threading').RLock()\n"
 rows={};patch=[]
 for name,oldfragment,newfragment,count in (('native_runtime.py',before,after,1),('test_actor_resources.py',fixture_before,fixture_after,2)):
  old=(B/name).read_text();assert old.count(oldfragment)==count
  new=old.replace(oldfragment,newfragment);assert new.count(newfragment)==count;assert new.replace(newfragment,oldfragment)==old;ast.parse(new)
  write(D/(name+'.proposed'),new.encode());rows[name]={'originalSHA256':sha(old.encode()),'proposedSHA256':sha(new.encode()),'originalMode':stat.S_IMODE((B/name).stat().st_mode),'wholeFileInverseExact':True,'replacements':count}
  patch+=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
 original=ast.parse((B/'native_runtime.py').read_text());proposed=ast.parse((D/'native_runtime.py.proposed').read_text());methods={}
 for cls in original.body:
  if isinstance(cls,ast.ClassDef):
   newcls=next(x for x in proposed.body if isinstance(x,ast.ClassDef)and x.name==cls.name)
   for fn in cls.body:
    if isinstance(fn,ast.FunctionDef)and not(cls.name=='NativeFactory'and fn.name=='housekeep'):
     assert ast.dump(fn,include_attributes=False)==ast.dump(next(x for x in newcls.body if isinstance(x,ast.FunctionDef)and x.name==fn.name),include_attributes=False);methods[cls.name+'.'+fn.name]=sha(ast.dump(fn,include_attributes=False).encode())
 for fn in original.body:
  if isinstance(fn,ast.FunctionDef):assert ast.dump(fn,include_attributes=False)==ast.dump(next(x for x in proposed.body if isinstance(x,ast.FunctionDef)and x.name==fn.name),include_attributes=False)
 write(D/'intended.patch',''.join(patch).encode());write(D/'intended-source-map.json',(json.dumps(rows,indent=2)+'\n').encode())
 write(D/'runtime-mapping.json',(json.dumps({'productDelta':'NativeFactory.housekeep perquery reentrant receipt admission','unchangedMethods':methods,'deadlineStartsAt':'unchanged ReadonlyIPC.query deadline=time.monotonic()+timeout, AFTER wrapper acquires journal_lock','deadlineIncludesPreRegistrationAuthority':True,'fixedQueries':['j/clients','/repl print(hl.plugin.hyprbars.window_families())','j/clients'],'allTimeoutsSeconds':[.6,.6,.6],'fixtureChanges':'two real RLock assembly statements; complete inverse exact','readonlyIPCUnchanged':True,'controllerManagerKeeperUnchanged':True,'nativeAccepted':False},indent=2)+'\n').encode())
 print(json.dumps(rows))
if __name__=='__main__':main()
