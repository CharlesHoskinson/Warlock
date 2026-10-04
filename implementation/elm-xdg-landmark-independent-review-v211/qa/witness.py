"""Read-only CPU characterization of actual held208 boundary acceptance."""
import ast,hashlib,importlib.util,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OLD=REPO/'implementation/elm-xdg-presented-landmark-oracle-v208';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=OLD/'component-manifest.json';assert sha(manifest)=='48fcb8bd0017ebf6924fcb1a484585bfbe3eb8f9d09b6196367ad6c7cedf7bb8'
m=json.loads(manifest.read_text())
for rel,row in m['files'].items():assert sha(OLD/rel)==row['sha256'],rel
spec=importlib.util.spec_from_file_location('actual208',OLD/'oracle.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
image=next(n for n in ast.parse((OLD/'qa/test.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='image');namespace={'m':module};exec(compile(ast.Module(body=[image],type_ignores=[]),str(OLD/'qa/test.py'),'exec'),namespace)
rows=[]
for name,serial,history in [('valid-control',87,[86,87]),('equal-float-history',87,[87.0]),('equal-bool-history',1,[True])]:
 rgb,w,h=namespace['image'](1,serial)
 result=module.inspect(rgb,w,h,[100,200],1,[120,220,100,80],[0,0,100,80],serial,observed_serials=history)
 rows.append({'name':name,'history':history,'historyTypes':[type(x).__name__ for x in history],'serial':serial,'accepted':len(result['samples'])==5,'nativeAcceptance':False})
assert all(r['accepted'] for r in rows)
out=ROOT/'witness.json';assert not out.exists();out.write_text(json.dumps({'passed':True,'scope':'Finding reproduced against actual held208 using its synthetic image function; not native capture or presentation acceptance','finding':'Noncanonical equal-valued float/bool observation history accepted','rows':rows,'source':str(OLD/'oracle.py'),'sourceSHA256':sha(OLD/'oracle.py'),'manifestSHA256':sha(manifest)},indent=2)+'\n')
print(json.dumps({'findingReproduced':True,'report':str(out),'reportSHA256':sha(out)}))
