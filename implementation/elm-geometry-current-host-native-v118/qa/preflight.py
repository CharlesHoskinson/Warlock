"""Execute the actual native runner's pre-GUI closure, preserving its campaign."""
import ast,hashlib,importlib.util,json,resource,shutil,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
PARENT=REPO/'implementation/elm-geometry-monitor-native-regression-v79'
HOST=REPO/'implementation/elm-geometry-current-private-host-links-v112'
OUT=ROOT/'qa'/('preflight-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'nativeAcceptance':False,'checks':[],
        'scope':'Original campaign AST and actual full pre-GUI runner closure; no GUI'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,value):
    report['checks'].append({'name':name,'passed':bool(value)});assert value,name
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def dump(node):return ast.dump(node,include_attributes=False)
try:
    original=ast.parse((PARENT/'qa/native.py').read_text());selected=ast.parse((ROOT/'qa/native.py').read_text())
    helpers=[n for n in original.body if isinstance(n,ast.FunctionDef)]
    for old in helpers:
        new=next(n for n in selected.body if isinstance(n,ast.FunctionDef) and n.name==old.name)
        check('exact original helper '+old.name,dump(old)==dump(new))
    oldtry=next(n for n in original.body if isinstance(n,ast.Try));newtry=next(n for n in selected.body if isinstance(n,ast.Try))
    oldwith=next(n for n in oldtry.body if isinstance(n,ast.With));newwith=next(n for n in newtry.body if isinstance(n,ast.With))
    oldcampaign=next(n for n in oldwith.body if isinstance(n,ast.Try));newcampaign=next(n for n in newwith.body if isinstance(n,ast.Try))
    check('entire original96 campaign body unchanged',dump(ast.Module(body=oldcampaign.body,type_ignores=[]))==dump(ast.Module(body=newcampaign.body,type_ignores=[])))
    check('original cleanup retained with explicit normal-exit and empty-native-client gates',all(name in (ROOT/'qa/native.py').read_text() for name in ['normalGeometryClientExitBeforePluginUnload','nativeGeometryClientsEmptyBeforePluginUnload','pluginUnloadedBeforeHostStop']))
    host=load('current_geometry_host_preflight',HOST/'candidate_host.py')
    helper=load('current_geometry_tuple_preflight',ROOT/'qa/tuple_preflight.py')
    context={'host':host,'FIXTURE':REPO/'implementation/elm-geometry-client-suspend-v53',
             'AUTH':REPO/'implementation/elm-parent-first-anchor-pair-v90','ROOT':HOST,'REPO':REPO,
             'Path':Path,'json':json,'report':report,'OUT':OUT,'__file__':str(ROOT/'qa/native.py'),
             'shutil':shutil,'verify_frozen_tuple':helper.verify_frozen_tuple,
             'ADAPTER':REPO/'implementation/elm-window-geometry-effect-adapter-v43/adapter'}
    prefix=newtry.body[:newtry.body.index(newwith)]
    exec(compile(ast.Module(body=prefix,type_ignores=[]),str(ROOT/'qa/native.py'),'exec'),context)
    check('actual current owning pre-GUI closure passed',context['core']['sha256']=='3e02556699f1e1667a88ace26f656ee380fce8a39b20d405a3f0d2757c65cd73')
    report['candidateSources']={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'qa/native.py',ROOT/'qa/tuple_preflight.py',Path(__file__),ROOT/'origins.json']}
    report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'checks':len(report['checks']),'error':report.get('error')}))
raise SystemExit(not report['passed'])
