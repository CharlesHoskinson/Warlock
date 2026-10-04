import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('hooks-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=ROOT/'candidate/src/backend/Wayland.cpp';text=source.read_text()
helper=text[text.index('struct PrivateParentKeyboard {'):text.index('// A lost parent cannot send physical releases.')]
surface_map=text[text.index('static std::unordered_map<wl_proxy*, CWaylandOutput*> keyboardOutputSurfaces;'):text.index('struct PrivateParentKeyboard {')]
ctor=text[text.index('Aquamarine::CWaylandKeyboard::CWaylandKeyboard('):text.index('Aquamarine::CWaylandKeyboard::~CWaylandKeyboard()')]
destructor=text[text.index('Aquamarine::CWaylandKeyboard::~CWaylandKeyboard()'):text.index('\nconst std::string& Aquamarine::CWaylandKeyboard::getName()')]
r={'passed':False,'nativeAcceptance':False,'scope':'Actual extracted keyboard constructor callbacks/private helpers/destructor; typed protocol adapter and real Hyprutils ownership/signals; actual capability callback retaining backend and native Core/GTK behavior separate','commands':[],'inputs':{str(p):sha(p) for p in [Path(__file__),source,ROOT/'qa/hooks-template.cpp']}}
def run(name,args,expected):
 p=subprocess.run(args,capture_output=True,timeout=90);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append({'name':name,'command':args,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True)
 assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-3000:];return p
try:
 template=(ROOT/'qa/hooks-template.cpp').read_text()
 def evaluate(name,h,c,expected):
  cpp=OUT/(name+'.cpp');cpp.write_text(template.replace('@@SURFACE_MAP@@',surface_map).replace('@@HELPER@@',h).replace('@@CONSTRUCTOR@@',c).replace('@@DESTRUCTOR@@',destructor));exe=OUT/name
  run(name+'-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-Wno-unused-parameter',str(cpp),'-lhyprutils','-o',str(exe)],0)
  return run(name+'-run',[str(exe)],expected)
 p=evaluate('candidate',helper,ctor,0);r['candidateChecks']=int(p.stdout.decode().split('checks: ')[1])
 mutants=[('missing-leave','ctor','        cancelHeldParentKeys(std::vector<SP<CWaylandKeyboard>>{*device});','        (void)surface;','leave cancels held key'),
  ('focus-not-cleared','helper','        state->second.focused = false;','','leave clears private focus and keys'),
  ('enter-not-admitted','ctor','        keyboardState[this].focused = true;','        keyboardState[this].focused = false;','owned enter invents no keys'),
  ('invented-enter-press','ctor','        keyboardState[this].focused = true;','        keyboardState[this].focused = true;\n        events.key.emit(SKeyEvent{.timeMs=100,.key=30,.pressed=true});','owned enter invents no keys'),
  ('late-key-admitted','ctor','!stateRecord->second.focused ||\n            (state !=','(state !=','late key and modifiers refused after leave'),
  ('key-not-retained','key','        const auto keepDevice = *device;','','key callback retains matched keyboard'),
  ('modifier-not-retained','modifiers','        const auto keepDevice = *device;','','modifier callback retains matched keyboard'),
  ('early-capability-retirement','helper','    cancelHeldParentKeys(keyboards);\n    keyboards.clear();','    keyboards.clear();\n    cancelHeldParentKeys(keyboards);','capability cancels before retirement')]
 for name,region,before,after,reason in mutants:
  h,c=helper,ctor
  if region=='helper':assert h.count(before)==1;h=h.replace(before,after)
  elif region=='ctor':assert c.count(before)==1;c=c.replace(before,after)
  else:
   start=c.index('    keyboard->set'+('Key(' if region=='key' else 'Modifiers('));end=c.index('\n    });',start)
   body=c[start:end];assert body.count(before)==1;c=c[:start]+body.replace(before,after)+c[end:]
  p=evaluate(name,h,c,1);assert ('FAIL '+reason).encode() in p.stderr
 for path,digest in r['inputs'].items():assert sha(path)==digest
 r.update(passed=True,candidateValidated=True,mutantsRejected=len(mutants),helperSHA256=hashlib.sha256(helper.encode()).hexdigest(),constructorSHA256=hashlib.sha256(ctor.encode()).hexdigest(),destructorSHA256=hashlib.sha256(destructor.encode()).hexdigest())
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
