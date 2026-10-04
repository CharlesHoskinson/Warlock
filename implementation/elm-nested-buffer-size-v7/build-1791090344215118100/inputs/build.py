import hashlib,json,resource,shlex,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1), 'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parent
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'installed':False,'commands':[],'scope':'Actual AQ dimension guard build; parent viewport/mode mapping remains open'}
def run(name,args):
 p=subprocess.run(args,capture_output=True,timeout=240)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 report['commands'].append({'name':name,'command':args,'exitCode':p.returncode})
 print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr.decode(errors='replace')[-4000:]
 return p
try:
 upstream=json.loads((ROOT/'upstream.json').read_text());parent=Path(upstream['parent'])
 assert digest(parent/'frozen-inputs.json')==upstream['parentInventorySHA256']
 def verify_parent():
  for rel,sha in upstream['sources'].items():assert digest(parent/'candidate'/rel)==sha,rel
 verify_parent()
 report['sources']={str(p.relative_to(ROOT/'candidate')):digest(p) for p in sorted((ROOT/'candidate').rglob('*')) if p.is_file()}
 report['upstreamSHA256']=digest(ROOT/'upstream.json');report['runnerSHA256']=digest(__file__)
 for p in sorted((parent/'candidate/include').rglob('*')):
  if p.is_file():assert digest(p)==digest(ROOT/'candidate/include'/p.relative_to(parent/'candidate/include'))
 report['publicHeadersUnchanged']=True
 run('guard-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-I'+str(ROOT/'candidate/src/backend'),str(ROOT/'test-dimensions.cpp'),'-o',str(OUT/'test-dimensions')])
 run('guard-tests',[str(OUT/'test-dimensions')])
 source=(ROOT/'candidate/src/backend/Wayland.cpp').read_text()
 guard=source.index('if (!NestedPolicy::validPixelDimensions')
 start=source.index('bool Aquamarine::CWaylandOutput::commit()')
 for marker in ('swapchain->reconfigure(', 'auto wlBuffer = wlBufferFromBuffer(', 'wlBuffer->pendingRelease = true;', 'waylandState.surface->sendAttach(wlBuffer', 'sched.onFrameSubmitted();'):
  assert start < guard < source.index(marker,start),marker
 report['rejectionBeforeCommitMutation']=True
 run('configure',['/usr/bin/cmake','-S',str(ROOT/'candidate'),'-B',str(OUT/'cmake'),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_INSTALL_PREFIX='+str(OUT/'prefix')])
 run('library-build',['/usr/bin/cmake','--build',str(OUT/'cmake'),'--target','aquamarine','-j','2'])
 library=OUT/'cmake/libaquamarine.so.0.15.0';assert library.is_file()
 report['library']=str(library);report['librarySHA256']=digest(library)
 dependency_paths={}
 for dep in (OUT/'cmake').rglob('*.o.d'):
  for path in shlex.split(dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]):
   path=Path(path)
   if not path.is_absolute():path=OUT/'cmake'/path
   if path.is_file():dependency_paths[str(path.resolve())]=digest(path)
 report['dependencies']=dependency_paths
 oldlib=parent/'prefix/lib/libaquamarine.so.0.15.0'
 def symbols(lib):
  proc=run('symbols-'+('parent' if lib==oldlib else 'candidate'),['/usr/bin/nm','-D','--defined-only',str(lib)])
  return {line.split()[-1] for line in proc.stdout.decode().splitlines() if line.split()}
 missing=sorted(symbols(oldlib)-symbols(library));report['missingParentSymbols']=missing;assert not missing,missing
 verify_parent();report['parentPreserved']=True;report['passed']=True
except Exception as e:report['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json',flush=True)
raise SystemExit(not report['passed'])
