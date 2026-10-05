import ast,hashlib,importlib.util,json,marshal,pathlib,resource,shutil,struct,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('wrapper-witness-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'characterizationOnly':True,'checks':[]}
try:
 for name in ('parent_loader.py','native.py','preflight.py'):(OUT/name).write_bytes((ROOT/'qa'/name).read_bytes())
 fixture=OUT/'fixture';(fixture/'qa').mkdir(parents=True)
 for p in (ROOT/'qa').glob('*.py'):shutil.copyfile(p,fixture/'qa'/p.name)
 shutil.copytree(ROOT/'qa/helpers',fixture/'qa/helpers')
 source=fixture/'qa/parent_loader.py';tree=ast.parse(source.read_bytes())
 target=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='checked_parent');target.body=[ast.Return(value=ast.Tuple(elts=[ast.Constant('unqualified-cache-callback'),ast.Dict(keys=[],values=[])],ctx=ast.Load()))];ast.fix_missing_locations(tree)
 code=compile(tree,str(source),'exec');st=source.stat();cache=pathlib.Path(importlib.util.cache_from_source(str(source)));cache.parent.mkdir();cache.write_bytes(importlib.util.MAGIC_NUMBER+struct.pack('<III',0,int(st.st_mtime)&0xffffffff,st.st_size)+marshal.dumps(code))
 driver=OUT/'driver.py';driver.write_text("import sys;sys.path[:0]=[sys.argv[1],sys.argv[1]+'/helpers'];import native,parent_loader;print(native.checked_parent(None,{}));assert native.checked_parent(None,{})==('unqualified-cache-callback',{})\n")
 p=subprocess.run(['/usr/bin/python3','-B',str(driver),str(fixture/'qa')],capture_output=True,timeout=8);(OUT/'cache.stdout').write_bytes(p.stdout);(OUT/'cache.stderr').write_bytes(p.stderr);assert p.returncode==0,(p.returncode,p.stderr.decode());r['checks'].append({'actualUnchangedNativeImportAcceptsAlteredExistingPyc':True,'noGUI':True})
 # Exact declared wrapper slot can also be replaced without code qualification.
 slot=OUT/'slot.py';slot.write_text("import sys;sys.path[:0]=[sys.argv[1],sys.argv[1]+'/helpers'];import parent_loader;parent_loader.checked_parent=lambda *args:('foreign-slot',{});import native;assert native.checked_parent(None,{})==('foreign-slot',{});print('foreign wrapper slot reached by actual native import')\n")
 cache.unlink();p=subprocess.run(['/usr/bin/python3','-B',str(slot),str(fixture/'qa')],capture_output=True,timeout=8);(OUT/'slot.stdout').write_bytes(p.stdout);(OUT/'slot.stderr').write_bytes(p.stderr);assert p.returncode==0,(p.returncode,p.stderr.decode());r['checks'].append({'foreignActualImportedWrapperSlotUnqualified':True,'noGUI':True});r['passed']=True
except BaseException as e:
 import traceback;r['error']=repr(e);r['traceback']=traceback.format_exc()
r['sourceSHA256']={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ('parent_loader.py','native.py','preflight.py')};r['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
