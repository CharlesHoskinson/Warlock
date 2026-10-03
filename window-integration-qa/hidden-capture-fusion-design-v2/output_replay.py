"""Actual private files exercise the exact unapplied output-availability guard."""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from qa_launch import require_qa_scope

def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
    scope=require_qa_scope();path=HERE/'native_desktop.py.proposed';original=path.read_text();sources={str(path):stamp(path),__file__:stamp(Path(__file__))}
    cls=next(n for n in ast.parse(original).body if isinstance(n,ast.ClassDef) and n.name=='NativeDesktop')
    method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_capture_hidden_fused')
    guard=next(n for n in ast.walk(method) if isinstance(n,ast.If) and any(isinstance(v,ast.Constant) and v.value=='incomplete hidden pixel outputs' for v in ast.walk(n)))
    assert 'path.is_file()' in ast.unparse(guard.test) and 'path.stat().st_size < 64' in ast.unparse(guard.test)
    slots=next(n for n in ast.walk(method) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='slot')
    replaces=[n.lineno for n in ast.walk(method) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='replace']
    assert guard.end_lineno<slots.lineno and all(guard.end_lineno<line for line in replaces)
    function=ast.FunctionDef(name='check',args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='temporary'),ast.arg(arg='composed')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=[guard,ast.Return(value=ast.Constant(value=True))],decorator_list=[])
    env={};exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),str(path),'exec'),env)
    cases=[]
    shapes=[('both missing',None,None,False),('thumbnail missing',None,64,False),('whole missing',64,None,False),('empty thumbnail',0,64,False),('short thumbnail',63,64,False),('empty whole',64,0,False),('short whole',64,63,False),('both minimal nonempty',64,64,True),('both larger nonempty',128,4096,True)]
    with tempfile.TemporaryDirectory(prefix='output-guard-',dir=HERE) as directory:
        root=Path(directory);root.chmod(0o700)
        for i,(name,thumbsize,wholesize,expected) in enumerate(shapes):
            sub=root/str(i);sub.mkdir(mode=0o700);thumb=sub/'thumbnail.png';whole=sub/'composed.png'
            for output,size in ((thumb,thumbsize),(whole,wholesize)):
                if size is not None:
                    with os.fdopen(os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')as f:f.write(b'x'*size)
            error=None
            try:observed=env['check'](thumb,whole)
            except ValueError as e:observed=False;error=str(e)
            assert observed==expected and (expected or error=='incomplete hidden pixel outputs')
            cases.append({'name':name,'thumbnailSize':thumbsize,'wholeSize':wholesize,'allowed':observed,'error':error})
    v1=HERE.with_name('hidden-capture-fusion-design-v1')/'native_desktop.py.proposed'
    delta="                    # Job closure does not prove both private files exist.\n                    if any(not path.is_file() or path.stat().st_size<64 for path in (temporary,composed)):\n                        raise ValueError('incomplete hidden pixel outputs')\n"
    assert original.count(delta)==1 and original.replace(delta,'')==v1.read_text()
    sources[str(v1)]=stamp(v1)
    assert sources=={p:stamp(Path(p))for p in sources}
    row={'result':'pass','scope':scope,'cases':cases,'exactCandidateGuardUsed':True,'availabilityBeforeEveryPublication':True,'onlyV1SourceDelta':delta,'v1WholeInverseExact':True,'sources':sources,'minimal64ByteBoundOnly':True,'ownedLaunchProof':False,'PNGPixelProof':'retained unchanged command V1 16 matrices/32 comparisons','nativeLaunch':False,'runtimeApplied':False}
    with os.fdopen(os.open(HERE/'output-replay.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'result':'pass','cases':len(cases),'wholeV1InverseExact':True,'report':str(HERE/'output-replay.json')}))

if __name__=='__main__':main()
