import ast,copy,json,os,pathlib,resource,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from preflight import sha,checked_guard,verify
import host_guard
OUT=ROOT/'qa'/('targeted-'+str(time.time_ns()));OUT.mkdir()
r={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(name,value):assert value,name;r['checks'].append({'name':name,'passed':True})
try:
    origin=json.loads((ROOT/'targeted-origin.json').read_text());old=pathlib.Path(origin['ancestor'])
    check('exact-held337',sha(old/'component-manifest.json')==origin['manifestSHA256'])
    for name in ('selector.py','stamp.py','target.py','join.py','map_failure.py','ancestor-shell.py','ancestor-observer_endpoint.py'):
        check('unchanged-'+name,(ROOT/'qa'/name).read_bytes()==(old/'qa'/name).read_bytes())
    for p in (old/'qa/helpers').glob('*.py'):check('unchanged-helper-'+p.name,(ROOT/'qa/helpers'/p.name).read_bytes()==p.read_bytes())
    original=ast.parse((old/'qa/native.py').read_text());current=__import__('timing_source').original_ast(ast.unparse(__import__('parent_source').original((ROOT/'qa/native.py').read_text())))
    expected=ast.parse("host_maps=host_guard.verify(guard,binary=host_binary,report=host_report,pid=web.pid,start=int(host_identity['start']),deadline=boot,directory=out/'host-map-failure',diagnostics=r)").body[0]
    old_check=next(n for n in ast.walk(original) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check' and isinstance(n.args[0],ast.Constant) and n.args[0].value=='actual-stamped-host-and-library-maps')
    new_check=ast.parse("check('actual-stamped-host-and-library-maps',host_maps['requiredArtifacts']==[str(host_binary)] and host_maps['mappedLibraryCount']==len(host_report['linkedLibraries']),maps=host_maps,identity=host_identity)").body[0].value
    counts={'import':0,'identity':0,'guard':0,'check':0,'fallback':0}
    class Restore(ast.NodeTransformer):
        def visit_Import(self,n):
            if any(a.name=='host_guard' for a in n.names):counts['import']+=1;n.names=[a for a in n.names if a.name!='host_guard']
            return n
        def visit_Assign(self,n):
            if ast.dump(n)==ast.dump(expected):counts['guard']+=1;return None
            if len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='host_identity':
                counts['identity']+=1;return [n,ast.parse('host_maps=host.original.mapped_files(web.pid)').body[0]]
            return n
        def visit_Call(self,n):
            if ast.dump(n)==ast.dump(new_check):counts['check']+=1;return copy.deepcopy(old_check)
            return self.generic_visit(n)
        def visit_If(self,n):
            expected_test=ast.parse("'sameReadMapFailure' not in r and 'mapFailureArchiveError' not in r and 'hostMapGuardRefusal' not in r",mode='eval').body
            if ast.dump(n.test)==ast.dump(expected_test):
                counts['fallback']+=1;n.test=ast.parse("'sameReadMapFailure' not in r and 'mapFailureArchiveError' not in r",mode='eval').body
            return self.generic_visit(n)
    restored=Restore().visit(copy.deepcopy(current))
    check('exact-five-declared-source-deltas',counts=={k:1 for k in counts})
    check('whole-native-body-restores-exact337',ast.dump(restored)==ast.dump(original))
    _,_,_,_,binary,_,files=verify();r['externalFiles']=files
    build=ROOT.parent/'elm-own-popup-host-surface-stamp-v310/qa/build-1791153652664233159/report.json'
    host=json.loads(build.read_text());check('exact144-required-host-libraries',len(host['linkedLibraries'])==144 and all(not pathlib.Path(p).is_symlink() for p in host['linkedLibraries']))
    guard,guard_files=checked_guard();r['guardFiles']=guard_files
    pid=os.getpid();start=guard.process_identity(guard.read_text_bounded('/proc/self/stat',65536),pid=pid)
    exe=pathlib.Path('/proc/self/exe').resolve();libc=pathlib.Path('/usr/lib/libc.so.6').resolve()
    report={'binarySHA256':sha(exe),'linkedLibraries':{str(libc):sha(libc)}}
    diagnostics={};result=host_guard.verify(guard,binary=exe,report=report,pid=pid,start=start,deadline=time.monotonic()+6,directory=OUT/'positive-unused',diagnostics=diagnostics)
    check('actual-process-targeted-executable-and-libc',result['requiredArtifacts']==[str(exe)] and result['mappedLibraryCount']==1 and not result['authenticatedHost'] and not result['nativeAcceptance'] and diagnostics=={})
    wrong={**report,'linkedLibraries':{**report['linkedLibraries'],'/usr/bin/true':sha('/usr/bin/true')}}
    for name,collision in (('missing-required',False),('archive-IO',True)):
        directory=OUT/name
        if collision:directory.mkdir()
        diagnostics={}
        try:host_guard.verify(guard,binary=exe,report=wrong,pid=pid,start=start,deadline=time.monotonic()+6,directory=directory,diagnostics=diagnostics)
        except guard.Refused as failure:
            check(name+'-original-required-mapping-refusal',str(failure)=='required runtime artifact absent: /usr/bin/true' and diagnostics['hostMapGuardRefusal']==repr(failure))
            if collision:check('archive-IO-secondary-only','FileExistsError' in diagnostics['hostMapFailureArchiveError'])
            else:check('same-read-host-bytes-and-owner',(directory/'maps.raw').read_bytes()==failure.map_evidence['raw'] and diagnostics['sameReadHostMapFailure']['pid']==pid and diagnostics['sameReadHostMapFailure']['start']==start)
        else:raise AssertionError('missing required host library accepted')
    diagnostics={}
    try:host_guard.verify(guard,binary=exe,report=report,pid=pid,start=start,deadline=time.monotonic()-1,directory=OUT/'expired-unused',diagnostics=diagnostics)
    except guard.Refused as failure:check('original-expired-deadline-not-reset',str(failure)=='original deadline exhausted' and failure.map_evidence is None and diagnostics['sameReadHostMapFailure'] is None)
    else:raise AssertionError('expired deadline accepted')
    r['sourceInputs']={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'qa').glob('*.py')};r['passed']=True
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
