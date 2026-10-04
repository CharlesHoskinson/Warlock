from pathlib import Path
import ast,copy,hashlib,importlib.util,json,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
helper=load('helper',ROOT/'qa/pointer.py');oracle=load('oracle',REPO/'implementation/elm-xdg-pointer-journal-oracle-v213/oracle.py')
checks=[]
def check(name,f,valid=True):
 try:f();passed=valid
 except (ValueError,AssertionError):passed=not valid
 checks.append({'name':name,'passed':passed});assert passed,name
pair=[{'event':'pointer-button','ownedSurface':True,'pid':19,'sequence':i+3,'button':272,'buttonState':1-i,'pointerSerial':80+i,'pointerTime':91+i,'local':[4,4],'localFixed':[1024,1024]} for i in range(2)]
call=lambda rows:helper.complete_pair(rows,2,pid=19,button=272,expected=[4,4],oracle=oracle)
check('completePair',lambda:call(pair))
check('motionDoesNotHideButton',lambda:call([{'event':'pointer-motion','sequence':3},*pair]))
for label,rows in [('extraOtherButton',[*pair,dict(pair[0],button=273,sequence=5)]),('foreignButton',[*pair,dict(pair[0],pid=20,sequence=5)]),('duplicate',[pair[0],*pair]),('missing',[pair[0]]),('reordered',pair[::-1]),('wrongLocal',[dict(pair[0],local=[5,4],localFixed=[1280,1024]),pair[1]]),('ownership',[dict(pair[0],ownedSurface=False),pair[1]])]:check(label,lambda rows=rows:call(rows),False)
check('prebaselineIgnored',lambda:call([dict(pair[0],sequence=1),*pair]))
check('cursorIndependentExact',lambda:helper.cursor_point({'x':83,'y':61},[83,61],oracle))
for value in ({'x':84,'y':61},{'x':True,'y':61},{'x':float('nan'),'y':61},{'x':83,'y':61,'recipient':19}):check('cursorReject'+repr(value),lambda value=value:helper.cursor_point(value,[83,61],oracle),False)
check('expiredOriginalDeadline',lambda:helper.deadline_guard(time.monotonic()-1),False)
check('remainingOriginalDeadline',lambda:helper.deadline_guard(time.monotonic()+1))
for path in (ROOT/'qa/native.py',ROOT/'qa/pixels.py',ROOT/'qa/pointer.py'):
 compile(path.read_bytes(),str(path),'exec');check('actualSyntax:'+path.name,lambda:None)
ancestor=ast.parse((ROOT/'original/native.py').read_text());candidate=ast.parse((ROOT/'qa/native.py').read_text())
old=[ast.dump(n,include_attributes=False) for n in ast.walk(ancestor) if isinstance(n,ast.Assert)]
new=[ast.dump(n,include_attributes=False) for n in ast.walk(candidate) if isinstance(n,ast.Assert)]
check('EveryOriginalAssertPreserved',lambda:None if all(n in new for n in old) else (_ for _ in ()).throw(AssertionError()))
check('ActualAQNormalizesSurfaceLocal',lambda:None if '.absolute = Vector2D{wl_fixed_to_double(x), wl_fixed_to_double(y)} / output->waylandState.surfaceSize' in (REPO/'implementation/elm-keyboard-focus-cancellation-v155/candidate/src/backend/Wayland.cpp').read_text() else (_ for _ in ()).throw(AssertionError()))
out=ROOT/'qa'/('test-'+str(time.time_ns()));out.mkdir()
sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),ROOT/'qa/native.py',ROOT/'qa/pointer.py',ROOT/'qa/pixels.py',ROOT/'original/native.py')}
report={'passed':True,'checks':checks,'inputs':sources,'nativeLaunched':False,'scope':'Actual helper boundary/syntax and preservation checks; no input delivery or pixel claim'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'report':str(out/'report.json')}))
