import ast,hashlib,json,os,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-hidden-capture-fusion-v29')
BASE=B.with_name('service-restore-focus-transaction-v28')
HERE=Path(__file__).resolve().parent
def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
 application=json.loads((HERE/'application.json').read_text());rows=[];changed=[]
 for name,row in application['copied'].items():
  old=BASE/name;new=B/name;assert stamp(old)==row
  current=stamp(new);assert current['mode']==row['mode']
  if current['sha256']!=row['sha256']:changed.append(name)
  rows.append({'name':name,'old':row,'new':current,'exact':row==current})
 assert sorted(changed)==['native_desktop.py','test_focus_transaction.py']
 source=(B/'native_desktop.py').read_text();tree=ast.parse(source)
 cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='NativeDesktop')
 method=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='_capture_hidden_fused')
 lines=source.splitlines(True);inverse=''.join(lines[:method.lineno-1]+lines[method.end_lineno:])
 old='                captured=self.base.capture(window,epoch)\n'
 new='                captured=self._capture_hidden_fused(window,epoch) if type(self.commands) is OwnedCommands and type(self.preview_batch) is BatchPreviews else self.base.capture(window,epoch)\n'
 assert inverse.count(new)==1 and inverse.replace(new,old)==(BASE/'native_desktop.py').read_text()
 fixture=(B/'test_focus_transaction.py').read_text();selection=application['fixtureChanged']['test_focus_transaction.py']
 assert fixture.count(selection['new'])==1 and fixture.replace(selection['new'],selection['old'])==(BASE/'test_focus_transaction.py').read_text()
 reviewed=Path('/home/hoskinson/window-integration-qa/hidden-capture-fusion-root-reviewed-v3/native_desktop.py.proposed')
 assert (B/'native_desktop.py').read_bytes()==reviewed.read_bytes()
 result={'result':'pass','inheritedFiles':len(rows),'inheritedExact':len(rows)-2,'declaredChanged':sorted(changed),
  'productChanged':['native_desktop.py'],'fixtureChanged':['test_focus_transaction.py'],'wholeProductInverseExact':True,'wholeFixtureLiteralInverseExact':True,
  'reviewedSource':{'path':str(reviewed),**stamp(reviewed)},'rows':rows,'runtimeAuthorityChangedElsewhere':False,'originalAll444BodiesAndAssertionsRetained':True,'nativeLaunch':False}
 path=HERE/'conservation.json'
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'result':'pass','inherited':len(rows),'exact':len(rows)-2,'changed':sorted(changed)}))
if __name__=='__main__':main()
