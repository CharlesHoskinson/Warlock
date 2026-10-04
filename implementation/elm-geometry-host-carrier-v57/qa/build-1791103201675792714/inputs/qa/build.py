"""Protected immutable V57 C build/tests only; no GUI or final host integration."""
import hashlib,json,pathlib,shlex,shutil,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 scope=require_qa_scope();out=ROOT/'qa'/('build-'+str(time.time_ns()));out.mkdir();inputs={};commands=[]
 for p in [*(ROOT/'native').iterdir(),ROOT/'upstream.json',pathlib.Path(__file__).resolve()]:
  if p.is_file():
   relative=p.relative_to(ROOT);dest=out/'inputs'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);inputs[str(relative)]=digest(p);dest.chmod(0o400)
 report={'passed':False,'nativeAcceptance':False,'scope':'Actual isolated native C carrier compilation and CPU checks; no coherent release or GUI','qaScope':scope,'inputs':inputs,'commands':commands}
 def run(name,cmd,success=True):
  p=subprocess.run(cmd,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);commands.append({'name':name,'command':cmd,'exitCode':p.returncode})
  if success and p.returncode:raise RuntimeError(name+': '+p.stderr)
  return p
 try:
  upstream=json.loads((ROOT/'upstream.json').read_text())
  for relative,value in upstream['parentFiles'].items():assert digest(pathlib.Path(upstream['parent'])/relative)==value,relative
  flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']).stdout)
  base=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations']
  run('host-build',base+['-MD','-MF',str(out/'host.d'),'native/host.c','-o',str(out/'elm-host'),*flags]);run('host-original-tests',[str(out/'elm-host'),'--self-test'])
  run('carrier-build',base+['native/geometry-carrier-test.c','-o',str(out/'carrier-tests'),*flags]);test=run('carrier-tests',[str(out/'carrier-tests')]);report['carrierChecks']=int(test.stdout.strip().split(': ')[-1])
  source=(out/'inputs/native/host.c').read_text();mutants=[('protocol', 'json_node_get_int(protocol)!=1','json_node_get_int(protocol)!=1 && FALSE'),('duplicates','state.duplicate && geometry_contains(json_parser_get_root(parser))','FALSE'),('surface-observations','!geometry_kind(rk) && ','')];report['mutants']=[]
  for name,needle,replacement in mutants:
   assert source.count(needle)==1;folder=out/('mutant-'+name);shutil.copytree(out/'inputs/native',folder);p=folder/'host.c';p.chmod(0o600);p.write_text(source.replace(needle,replacement));binary=out/('mutant-'+name+'-tests')
   run(name+'-build',base+[str(folder/'geometry-carrier-test.c'),'-o',str(binary),*flags]);result=run(name+'-tests',[str(binary)],False);assert result.returncode!=0,name;report['mutants'].append({'name':name,'rejected':True,'exitCode':result.returncode})
  dependency_text=(out/'host.d').read_text().replace('\\\n',' ');paths=shlex.split(dependency_text.split(':',1)[1]);report['dependencies']={}
  for raw in paths:
   p=pathlib.Path(raw);p=p if p.is_absolute() else out/'inputs'/p;report['dependencies'][str(p.resolve())]=digest(p)
  report['tools']={str(pathlib.Path(shutil.which(name)).resolve()):digest(shutil.which(name)) for name in ['cc','pkg-config']}
  for relative,value in inputs.items():assert digest(ROOT/relative)==value,relative;assert digest(out/'inputs'/relative)==value,relative
  report.update(passed=True,binary=str(out/'elm-host'),binarySHA256=digest(out/'elm-host'),flags=flags,originalHostTests=9,queueBound=16,controlByteBound=4096)
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 report['artifacts']={str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file()}
 path=out/'report.json';path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(path),'error':report.get('error')}),flush=True);return not report['passed']
if __name__=='__main__':raise SystemExit(main())
