import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('cancel-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=ROOT/'candidate/src/backend/Wayland.cpp';text=source.read_text()
helper=text[text.index('static void cancelHeldParentButtons('):text.index('\nstatic bool mappingReady(')]
destructor=text[text.index('Aquamarine::CWaylandPointer::~CWaylandPointer()'):text.index('\nconst std::string& Aquamarine::CWaylandPointer::getName()')]
r={'passed':False,'nativeAcceptance':False,'scope':'Actual cancellation helper and pointer destructor with real Hyprutils ownership and typed signals; native recipient/core state acceptance separate','commands':[],'inputs':{str(p):sha(p) for p in [Path(__file__),source,ROOT/'qa/cancel-template.cpp']}}
def run(name,args,expected):
 p=subprocess.run(args,capture_output=True,timeout=90);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':args,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-2500:];return p
try:
 template=(ROOT/'qa/cancel-template.cpp').read_text()
 def evaluate(name,body,expected):
  cpp=OUT/(name+'.cpp');cpp.write_text(template.replace('@@HELPER@@',body).replace('@@DESTRUCTOR@@',destructor));exe=OUT/name
  run(name+'-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-I'+str(ROOT/'candidate/src/backend'),str(cpp),'-lhyprutils','-o',str(exe)],0)
  return run(name+'-run',[str(exe)],expected)
 p=evaluate('candidate',helper,0);r['candidateChecks']=int(p.stdout.decode().split('checks: ')[1])
 mutants=[('missing-cancel','            pointer->events.button.emit(IPointer::SButtonEvent{.timeMs = now, .button = button, .pressed = false});','            (void)now;','only admitted held buttons cancelled'),
 ('invented-press','.pressed = false','.pressed = true','no synthesized press'),
 ('not-precleared','        state->second.held.fill(0);','','clear before callback'),
 ('missing-frame','        if (emitted) pointer->events.frame.emit();','        (void)emitted;','one frame for cancellation batch'),
 ('wrong-button','.button = button','.button = button + 1','only admitted held buttons cancelled')]
 for name,before,after,reason in mutants:
  assert helper.count(before)==1;broken=helper.replace(before,after);p=evaluate(name,broken,1);assert ('FAIL '+reason).encode() in p.stderr
 for path,digest in r['inputs'].items():assert sha(path)==digest
 r.update(passed=True,candidateValidated=True,mutantsRejected=len(mutants),helperSHA256=hashlib.sha256(helper.encode()).hexdigest(),destructorSHA256=hashlib.sha256(destructor.encode()).hexdigest())
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
