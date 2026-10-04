"""Qualify current tuple adapter source and closure without launching a GUI."""
import ast
import hashlib
import importlib.util
import json
import resource
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PARENT=REPO/'implementation/elm-geometry-staged-menu-native-v77'
OUT=ROOT/'qa'/('preflight-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'nativeAcceptance':False,'checks':[],
        'scope':'Exact current tuple adapter closure and unchanged protected host implementation; no GUI'}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check(name,value):
    report['checks'].append({'name':name,'passed':bool(value)})
    assert value,name
def node(tree,name):return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
def dump(value):return ast.dump(value,include_attributes=False)

try:
    inputs=[ROOT/'candidate_host.py',ROOT/'core_host.py',ROOT/'native-build-report.json',ROOT/'aq-tuple.json',ROOT/'source-origins.json',Path(__file__)]
    report['inputs']={str(p):sha(p) for p in inputs}
    for p in inputs:
        destination=OUT/'inputs'/p.relative_to(ROOT);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,destination)
    origins=json.loads((ROOT/'source-origins.json').read_text())
    for row in origins['origins']:check('source origin '+Path(row['path']).name,sha(Path(row['path']))==row['sha256'])
    for file,names in [('core_host.py',['ReviewedWestonHost','PrivateHyprSession','verify_inputs','aq_tuple']),('candidate_host.py',['ReviewedWestonHost','PrivateHyprSession','input_tuple'])]:
        old=ast.parse((PARENT/file).read_text());new=ast.parse((ROOT/file).read_text())
        for name in names:check('protected implementation exact '+file+':'+name,dump(node(old,name))==dump(node(new,name)))
    spec=importlib.util.spec_from_file_location('current_geometry_private_host',ROOT/'candidate_host.py')
    host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
    core=host.base.core_tuple();pair=host.pair_tuple();aq,library=host.base.aq_tuple();module,client,parent=host.input_tuple()
    check('current owning core89 selected',core['sha256']=='3e02556699f1e1667a88ace26f656ee380fce8a39b20d405a3f0d2757c65cd73')
    check('current core component closure selected',core['coreComponentManifestSHA256']=='4f10f5f3fba7f3186e7c9fdb13e45ad7bc2b08614755d081f8e620986f34d5fb')
    check('plugin90 owns exact core89',pair['nativePair']['core']=={'path':core['binary'],'sha256':core['sha256']} and 'elm-parent-first-anchor-pair-v90' in pair['nativePair']['plugin']['path'])
    check('current AQ105 selected',aq['librarySHA256']=='b7431f7036d28ed1f87a1aec9374a7700a2ebb9e819a707f0e8368a87cfcff97' and sha(library)==aq['librarySHA256'])
    check('fixed original parent input selected',parent['nativeChecks']==105 and module.is_file() and client.is_file())
    report['tuple']={'core':pair['nativePair']['core'],'plugin':pair['nativePair']['plugin'],'aquamarine':aq,'parentInputManifest':host.EXPECTED_INPUT_MANIFEST}
    for path,expected in report['inputs'].items():check('source stable '+Path(path).name,sha(Path(path))==expected)
    report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'checks':len(report['checks']),'error':report.get('error')}))
raise SystemExit(not report['passed'])
