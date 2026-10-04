import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
original=ROOT.parent/'elm-seat-publication-v79/candidate/src/backend/Wayland.cpp';candidate=ROOT/'candidate/src/backend/Wayland.cpp'
r={'passed':False,'nativeAcceptance':False,'scope':'Actual dispatch/poll/output destroy/destructor/frame-idle bodies with real Hyprutils weak/shared ownership; typed transport/core protocol fixtures; native transport and full refinement separate','commands':[],'inputs':{str(p):sha(p) for p in [Path(__file__),ROOT/'qa/template.cpp',original,candidate]}}
def run(name,args,expected):
 p=subprocess.run(args,capture_output=True,timeout=90);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':args,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-2500:];return p
def bodies(text):
 def body(start,end):return text[text.index(start):text.index(end,text.index(start))]
 return {'DISPATCH':body('bool Aquamarine::CWaylandBackend::dispatchEvents()','\nuint32_t Aquamarine::CWaylandBackend::capabilities()'),
 'POLL':body('std::vector<Hyprutils::Memory::CSharedPointer<SPollFD>> Aquamarine::CWaylandBackend::pollFDs()','\nbool Aquamarine::CWaylandBackend::dispatchEvents()'),
 'DESTROY':body('bool Aquamarine::CWaylandOutput::destroy()','\nbool Aquamarine::CWaylandOutput::test()'),
 'DESTRUCTOR':body('Aquamarine::CWaylandOutput::~CWaylandOutput()','\nstd::vector<SDRMFormat> Aquamarine::CWaylandOutput::getRenderFormats()'),
 'SCHEDULE':body('void Aquamarine::CWaylandOutput::scheduleFrame(', '\nAquamarine::CWaylandBuffer::CWaylandBuffer('),
 'FRAME':body('    frameIdle = makeShared<std::function<void(void)>>(','\n    waylandState.surface = ')}
try:
 template=(ROOT/'qa/template.cpp').read_text()
 def evaluate(name,parts,expected):
  source=template
  for token,value in parts.items():source=source.replace('@@'+token+'@@',value)
  assert '@@' not in source
  cpp=OUT/(name+'.cpp');cpp.write_text(source);exe=OUT/name
  run(name+'-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-I'+str(ROOT/'candidate/src/backend'),str(cpp),'-lhyprutils','-o',str(exe)],0)
  return run(name+'-run',[str(exe)],expected)
 old=evaluate('original',bodies(original.read_text()),1);assert b'FAIL actual vectors retired' in old.stderr
 parts=bodies(candidate.read_text());result=evaluate('candidate',parts,0)
 r['candidateChecks']=int(result.stdout.decode().split('checks: ')[1])
 mutants=[('devices','DISPATCH','        pointers.clear();\n        keyboards.clear();','', 'actual vectors retired'),
 ('descriptor','POLL',' || failedParentTransports.contains(this)','', 'failed descriptor withdrawn'),
 ('focus','DISPATCH','        focusedOutput = {};\n        lastEnterSerial = 0;','', 'focus and serial retired'),
 ('publication','DISPATCH','        lastEnterSerial = 0;\n        idleCallbacks.clear();','        lastEnterSerial = 0;', 'queued publication discarded'),
 ('frame-copy','FRAME','        if (!lifecycle->bufferAllowed())\n            return;','', 'copied frame task fenced'),
 ('late-frame','SCHEDULE','    const auto lifecycle = outputLifecycle.find(this);\n    if (lifecycle == outputLifecycle.end() || !lifecycle->second->bufferAllowed())\n        return;','','late frame scheduling refused'),
 ('output-once','DESTROY',' || !retiredOutputs.insert(this).second','', 'reentrant output retirement refused')]
 for name,token,before,after,failure in mutants:
  assert parts[token].count(before)==1
  altered=dict(parts);altered[token]=altered[token].replace(before,after)
  p=evaluate(name,altered,1);assert ('FAIL '+failure).encode() in p.stderr
 for path,digest in r['inputs'].items():assert sha(path)==digest
 r.update(passed=True,candidateValidated=True,mutantsRejected=len(mutants),originalViolation='actual vectors retired')
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
