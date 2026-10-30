#!/usr/bin/env python3
"""Actual proposed native owner tests and authority ABI build; no plugin load."""
import hashlib,json,os,re,shlex,shutil,subprocess,sys,time,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild');D=B/'native-cancellation-root-stage1-v3';A=B/'native-cancellation-astra-integration-v1/authority.cpp'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 sys.path.insert(0,str(R/'window-integration-qa'))
 from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise RuntimeError('Protected no-argument no-bytecode required')
 out=B/('native-cancellation-compiled-'+str(time.time_ns()));out.mkdir(mode=0o700)
 report={'passed':False,'nativeAcceptance':False,'pluginLoaded':False,'scope':scope,'commands':[]}
 env=dict(os.environ);env.update(PYTHONDONTWRITEBYTECODE='1',LC_ALL='C',TZ='UTC',PKG_CONFIG_PATH=str(B/'prefix/lib/pkgconfig'),LD_LIBRARY_PATH=str(B/'prefix/lib'))
 def run(name,args):
  args=list(map(str,args));stdout=out/(name+'.stdout');stderr=out/(name+'.stderr')
  try:p=subprocess.run(args,capture_output=True,env=env,timeout=240)
  except subprocess.TimeoutExpired as e:
   stdout.write_bytes(e.stdout or b'');stderr.write_bytes(e.stderr or b'');report['commands'].append({'name':name,'argv':args,'exitCode':None,'timedOut':True});raise
  stdout.write_bytes(p.stdout);stderr.write_bytes(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode,'stdoutSHA256':sha(stdout),'stderrSHA256':sha(stderr)})
  print(name,p.returncode,flush=True)
  if p.returncode:raise RuntimeError(name+' failed; diagnostics retained')
  return p.stdout.decode()
 try:
  receipt=B/'authority/authority-build-report.json';assert sha(receipt)=='efa8ad035d2f9bb9a2864f091407df0bdb97685dfae6e512b914a9f32c06280b';old=json.loads(receipt.read_text())
  plan=json.loads((B/'native-cancellation-root-v1/authority-build-plan.json').read_text());oldInputs={**old['inputs'],**old['dependencies'],**old['providerHashes'],**plan['tools']}
  proposed={str(p):sha(p) for p in [A,D/'native/effect_cancellation.hpp',D/'native/effect_cancellation_parser.hpp',D/'qa/effect_cancellation_test.cpp',Path(__file__).resolve()]}
  assert proposed[str(A)]=='2730c6e3605ae4a0c0ed2bc75eae1282854e2ffde369386f6992968e26a262e5'
  def check():
   for n,h in {**oldInputs,**proposed}.items():assert sha(n)==h,n
  check();report.update(originalReceipt={'path':str(receipt),'sha256':sha(receipt)},unchangedInputs=oldInputs,proposedInputs=proposed,owningCore=old['core'],owningAquamarine=old['aquamarine'],inputValidation='passed before first compiler invocation')
  stage=out/'inputs';(stage/'qa').mkdir(parents=True)
  copied={}
  for p in (B/'authority/inputs').rglob('*'):
   if not p.is_file():continue
   assert sha(p) in set(oldInputs.values()),p
   target=stage/p.relative_to(B/'authority/inputs');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);copied[str(target)]={'from':str(p),'sha256':sha(p)}
  shutil.copyfile(A,stage/'native/authority.cpp')
  for name in ['effect_cancellation.hpp','effect_cancellation_parser.hpp']:shutil.copyfile(D/'native'/name,stage/'native'/name)
  shutil.copyfile(D/'qa/effect_cancellation_test.cpp',stage/'qa/effect_cancellation_test.cpp')
  flags=shlex.split(run('json-cflags',['/usr/bin/pkg-config','--cflags','json-glib-1.0']))
  libs=shlex.split(run('json-libs',['/usr/bin/pkg-config','--libs','json-glib-1.0']))
  test=out/'effect-cancellation-test';run('owner-test-compile',['/usr/bin/g++','-std=c++23','-O2','-Wall','-Wextra','-Werror',*flags,stage/'qa/effect_cancellation_test.cpp','-o',test,*libs]);report['ownerResult']=json.loads(run('owner-test',[test]));assert report['ownerResult']['passed']
  # Compile the exact production formatter body, not a mock formatter.
  authority=(stage/'native/authority.cpp').read_text();body=authority[authority.index('// No untrusted strings are interpolated.'):authority.index('// The preparation resource is Owner')]
  wire=stage/'qa/real_wire_test.cpp';wire.write_text('#include "../native/effect_cancellation.hpp"\n#include <json-glib/json-glib.h>\n#include <cstdio>\n#include <cstring>\n#include <limits>\n#include <stdexcept>\nnamespace Cancellation=warlock::cancellation;\n'+body+'''\nint main(){try {
    using namespace Cancellation;
    Key k{{1,101,1,1,3},1,{1,1,4,1,3,5,6,Intent::Operation::Restore}};
    unsigned checks=0;
    auto ensure=[&](bool v){++checks;if(!v)throw std::runtime_error("real formatter assertion");};
    for(auto phase:{Phase::Prepared,Phase::Cancelled,Phase::Committed,Phase::Refused,Phase::ExecutionUnknown}) {
        Buffer b{};ensure(formatCancellation(b,k,17,100,phase,{8,9,phase==Phase::Cancelled?Reason::Cancelled:Reason::Applied,nullptr}));
        JsonParser* p=json_parser_new();GError* e=nullptr;ensure(json_parser_load_from_data(p,b.data.data(),b.size,&e));
        auto* o=json_node_get_object(json_parser_get_root(p));ensure(json_object_get_int_member(o,"cancellationProtocol")==1 && json_object_get_int_member(o,"effectProtocol")==1);
        ensure(!std::strcmp(json_object_get_string_member(o,"preparedId"),"17") && !std::strcmp(json_object_get_string_member(o,"deadlineMonotonicNs"),"100"));
        auto* binding=json_object_get_object_member(o,"binding");ensure(!std::strcmp(json_object_get_string_member(binding,"frontend"),"3"));
        auto* intent=json_object_get_object_member(o,"intent");ensure(!std::strcmp(json_object_get_string_member(intent,"operation"),"restore"));
        if(phase!=Phase::Prepared) {const char* expected=phase==Phase::Cancelled?"Cancelled":phase==Phase::Committed?"Committed":phase==Phase::Refused?"Refused":"Unknown";ensure(!std::strcmp(json_object_get_string_member(o,"status"),expected));ensure(!std::strcmp(json_object_get_string_member(o,"revision"),"8"));}
        g_object_unref(p);
    }
    Buffer b{};ensure(!formatCancellation(b,k,0,100,Phase::Prepared,{}));ensure(!formatCancellation(b,k,17,0,Phase::Prepared,{}));ensure(!formatCancellation(b,k,17,100,Phase::Committed,{}));
    ensure(!formatCancellation(b,k,17,100,Phase::Refused,{8,9,Reason::NativeRefusal,"bad\\\"reason"}));
    ensure(!formatCancellation(b,k,17,100,Phase::Refused,{8,9,Reason::NativeRefusal,nullptr}));
    k.owner.lifetime=k.intent.lifetime=k.owner.session=k.owner.frontend=k.intent.epoch=k.intent.request=k.intent.generation=k.intent.incarnation=k.intent.output=k.intent.revision=std::numeric_limits<U>::max();
    ensure(formatCancellation(b,k,std::numeric_limits<U>::max(),std::numeric_limits<U>::max(),Phase::Committed,{std::numeric_limits<U>::max(),std::numeric_limits<U>::max(),Reason::Applied,nullptr}));
    ensure(b.size<b.data.size());
    std::printf("{\\\"passed\\\":true,\\\"checks\\\":%u}\\n",checks);return 0;
} catch(const std::exception& e) {std::fprintf(stderr,"%s\\n",e.what());return 1;}}
''')
  real=out/'real-wire-test';run('real-wire-compile',['/usr/bin/g++','-std=c++23','-O2','-Wall','-Wextra','-Werror',*flags,wire,'-o',real,*libs]);report['wireResult']=json.loads(run('real-wire-test',[real]));assert report['wireResult']['passed']
  binary=out/'elm-window-geometry-authority.so';dep=out/'authority.d';args=plan['retainedRecipeArgv'];replacements={str(B/'authority/inputs/candidate'):str(stage/'candidate'),str(B/'authority/inputs/native/authority.cpp'):str(stage/'native/authority.cpp'),str(B/'authority/authority.d'):str(dep),str(B/'authority/elm-window-geometry-authority.so'):str(binary)}
  argv=[]
  for arg in args:
   for oldpath,newpath in replacements.items():arg=arg.replace(oldpath,newpath)
   argv.append(arg)
  run('authority-compile',argv)
  dependencies={str(Path(p).resolve()):sha(p) for p in shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1])}
  report.update(dependencies=dependencies,binary=str(binary),binarySHA256=sha(binary),copiedInputs=copied)
  pluginLoader=run('plugin-ldd',['/usr/bin/ldd',binary]);coreLoader=run('core-ldd',['/usr/bin/ldd',old['core']['path']]);assert 'not found' not in pluginLoader+coreLoader
  providers={Path(old['core']['path']).resolve()}
  for line in (pluginLoader+'\n'+coreLoader).splitlines():
   m=re.search(r'(?:=>\s+|^\s*)(/\S+)\s+\(',line)
   if m:providers.add(Path(m.group(1)).resolve())
  assert {str(p):sha(p) for p in providers}==old['providerHashes'],'Actual provider identities differ'
  exports=set()
  for i,p in enumerate(sorted(providers)):
   for line in run('provider-%03d'%i,['/usr/bin/nm','-D','--defined-only',p]).splitlines():
    words=line.split()
    if len(words)>=3:
     symbol=words[-1];exports.add(symbol.replace('@@','@'))
     if '@@' in symbol:exports.add(symbol.split('@')[0])
  undefined=run('undefined',['/usr/bin/nm','-D','--undefined-only',binary]);strong=[words[1] for line in undefined.splitlines() if len(words:=line.split())==2 and words[0]=='U'];missing=[s for s in strong if s not in exports];assert not missing,missing
  check()
  for n,h in dependencies.items():assert sha(n)==h,n
  report.update(passed=True,strongUndefined=strong,missingSymbols=missing,providerHashes=old['providerHashes'],staticClosureOnly=True)
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 report['outputs']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}),flush=True);return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
