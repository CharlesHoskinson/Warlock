import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('keys-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=ROOT/'candidate/src/backend/Wayland.cpp';text=source.read_text()
helper=text[text.index('struct PrivateParentKeyboard {'):text.index('// A lost parent cannot send physical releases.')]
destructor=text[text.index('Aquamarine::CWaylandKeyboard::~CWaylandKeyboard()'):text.index('\nconst std::string& Aquamarine::CWaylandKeyboard::getName()')]
r={'passed':False,'nativeAcceptance':False,'scope':'Actual private key admission/cancellation helper and keyboard destructor; real Hyprutils ownership/typed signals; native callback wiring and Core ledgers separate','commands':[],'inputs':{str(p):sha(p) for p in [Path(__file__),source,ROOT/'qa/keys-template.cpp']}}
def run(name,args,expected):
 p=subprocess.run(args,capture_output=True,timeout=90);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append({'name':name,'command':args,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True)
 assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-2500:];return p
try:
 template=(ROOT/'qa/keys-template.cpp').read_text()
 def evaluate(name,body,expected):
  cpp=OUT/(name+'.cpp');cpp.write_text(template.replace('@@HELPER@@',body).replace('@@DESTRUCTOR@@',destructor));exe=OUT/name
  run(name+'-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror',str(cpp),'-lhyprutils','-o',str(exe)],0)
  return run(name+'-run',[str(exe)],expected)
 p=evaluate('candidate',helper,0);r['candidateChecks']=int(p.stdout.decode().split('checks: ')[1])
 mutants=[('missing-release','            keyboard->events.key.emit(IKeyboard::SKeyEvent{.timeMs = now, .key = key, .pressed = false});','            (void)now;','modifier reset follows releases'),
 ('invented-press','.pressed = false','.pressed = true','no invented key press'),
 ('not-precleared','        state->second.held.fill(false);','','clear before callback'),
 ('missing-modifiers','        if (emitted || hadModifiers) keyboard->events.modifiers.emit(IKeyboard::SModifiersEvent{});','        (void)emitted; (void)hadModifiers;','one modifier reset per batch'),
 ('wrong-key','.key = key','.key = key + 1','modifier reset follows releases'),
 ('duplicate-admission','    if (state.held[key] == pressed) return false;','','duplicate key down refused'),
 ('modifier-only','if (emitted || hadModifiers)','if (emitted || (hadModifiers && false))','modifier only cancellation')]
 for name,before,after,reason in mutants:
  assert helper.count(before)==1;broken=helper.replace(before,after);p=evaluate(name,broken,1);assert ('FAIL '+reason).encode() in p.stderr
 for path,digest in r['inputs'].items():assert sha(path)==digest
 r.update(passed=True,candidateValidated=True,mutantsRejected=len(mutants),helperSHA256=hashlib.sha256(helper.encode()).hexdigest(),destructorSHA256=hashlib.sha256(destructor.encode()).hexdigest())
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
