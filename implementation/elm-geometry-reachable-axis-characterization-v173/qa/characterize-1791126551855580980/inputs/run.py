import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('characterize-'+str(time.time_ns()));(OUT/'inputs').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=REPO/'implementation/elm-geometry-constraint-coordinate-review-v155/reviewed-inputs.json'
provenance=json.loads(review.read_text());pair=REPO/'implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json';pd=json.loads(pair.read_text())
for name,row in provenance['files'].items():assert sha(Path(name))==row['sha256'],name
def source(suffix):
 p=next(Path(x) for x in provenance['files'] if x.endswith(suffix));shutil.copy2(p,OUT/'inputs'/p.name);return p.read_text()
def body(text,anchor):
 start=text.index(anchor);i=text.index('{',start);opening=i;i+=1;level=1
 while level:
  if text[i]=='{':level+=1
  elif text[i]=='}':level-=1
  i+=1
 return text[opening+1:i-1]
target=source('/layout/target/WindowTarget.cpp');base=source('/layout/target/Target.cpp');window=source('/desktop/view/Window.cpp')
maxbody=body(target,'} else if (FSMODES.internal == Fullscreen::FSMODE_MAXIMIZED)')
# The owning updatePos common finalization immediately follows the MAX arm.
maxbody+='\n m_window->updateWindowDecos();if(CONFIGURECLIENT)m_window->sendWindowSize();\n'
ordinary=body(target,'if (floating() && m_window && !Fullscreen::controller()->isFullscreen(m_window.lock()))')
roundbody=body(base,'void ITarget::setPositionGlobal(const STargetBox& box, uint8_t)')
report=body(window,'Vector2D CWindow::realToReportSize()');report=report[:report.index('    static auto PXWLFORCESCALEZERO')]+ '\n throw 1; // Uncharacterized X11 path is explicit refusal.\n'
for key,value in {'MAX':maxbody,'ordinary':ordinary,'round':roundbody,'report-Wayland':report}.items():(OUT/'inputs'/(key+'.txt')).write_text(value)
prelude=r'''#include <hyprutils/math/Box.hpp>
#include <cmath>
#include <climits>
#include <limits>
#include <iostream>
#include <iomanip>
#include <set>
using Hyprutils::Math::CBox;using Hyprutils::Math::Vector2D;using Hyprutils::Math::SBoxExtents;
namespace Math {constexpr const Vector2D VECTOR2D_MAX={std::numeric_limits<double>::max(),std::numeric_limits<double>::max()};}
struct Goal{Vector2D value;Vector2D goal(){return value;}Vector2D* operator->(){return &value;}};
struct CWindow{bool m_isX11=false;Goal g;Goal* m_realSize=&g;CBox box;Vector2D configured;SBoxExtents reserved;
SBoxExtents getFullWindowReservedArea(){return reserved;}void setBox(CBox b){box=b;g.value=b.size();}void updateWindowDecos(){}void sendWindowSize(){configured=realToReportSize();}Vector2D realToReportSize();};
struct STargetBox{CBox logicalBox,visualBox;};
struct CWindowTarget{STargetBox m_box;CWindow* m_window;void setPositionGlobal(const STargetBox& box);void maximize(bool CONFIGURECLIENT);void ordinary(bool CONFIGURECLIENT);};
'''
sourcecode=prelude+'Vector2D CWindow::realToReportSize(){'+report+'}\nvoid CWindowTarget::setPositionGlobal(const STargetBox& box){'+roundbody+'}\nvoid CWindowTarget::maximize(bool CONFIGURECLIENT){'+maxbody+'}\nvoid CWindowTarget::ordinary(bool CONFIGURECLIENT){'+ordinary+'}\n'+(ROOT/'qa/cases.cpp').read_text()
for p,h in pd['dependencies'].items():
 if '/hyprutils/' in p:assert sha(Path(p))==h,p
library=Path('/usr/lib/libhyprutils.so.0.14.2');assert sha(library)==pd['linkedLibraries'][str(library)]
originals={str(p):sha(p) for p in [ROOT/'spec/REQUIREMENTS.md',ROOT/'qa/cases.cpp',Path(__file__),review,pair,library,Path('/usr/bin/c++')]}
for p in [ROOT/'spec/REQUIREMENTS.md',ROOT/'qa/cases.cpp',Path(__file__)]:shutil.copy2(p,OUT/'inputs'/p.name)
r={'passed':False,'scope':'Actual owning arithmetic characterization only; no native/model/production acceptance','inputs':originals,'commands':[],'controls':[]}
try:
 for name,code in [('actual',sourcecode),('unsafe-bare-logical',sourcecode.replace('CBox visualBox = m_box.visualBox.empty() ? nodeBox : m_box.visualBox;','CBox visualBox = nodeBox;')),('unsafe-ordinary-reserve',sourcecode.replace('m_window->setBox(m_box.logicalBox);','m_window->setBox(CBox{m_box.logicalBox.pos()+m_window->reserved.topLeft,m_box.logicalBox.size()-(m_window->reserved.topLeft+m_window->reserved.bottomRight)});'))]:
  cpp=OUT/(name+'.cpp');cpp.write_text(code);cmd=['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-MMD','-MF',str(OUT/(name+'.d')),str(cpp),'-lhyprutils','-o',str(OUT/name)]
  c=subprocess.run(cmd,capture_output=True,timeout=30);(OUT/(name+'-compile.stderr')).write_bytes(c.stderr);r['commands'].append({'command':cmd,'exitCode':c.returncode});assert c.returncode==0,c.stderr.decode()
  c=subprocess.run([str(OUT/name)],capture_output=True,timeout=5);(OUT/(name+'.stdout')).write_bytes(c.stdout);(OUT/(name+'.stderr')).write_bytes(c.stderr)
  if name=='actual':assert c.returncode==0,c.stdout.decode();r['checks']=int(c.stdout.decode().split('TOTAL ')[1].split()[0])
  else:
   assert c.returncode!=0 and b'FAIL ' in c.stdout;caught=[line[5:] for line in c.stdout.decode().splitlines() if line.startswith('FAIL ')];r['controls'].append({'name':name,'rejected':True,'failures':caught})
 deps=set()
 for d in OUT.glob('*.d'):
  names=shlex.split(d.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]);deps.update(Path(x).resolve() for x in names)
 r['compilerDependencies']={str(p):sha(p) for p in sorted(deps)}
 l=subprocess.run(['/usr/bin/ldd',str(OUT/'actual')],capture_output=True,timeout=5);assert l.returncode==0;(OUT/'ldd.stdout').write_bytes(l.stdout)
 r['linkedLibraries']={str(Path(line.split('=>',1)[1].strip().split()[0]).resolve()):sha(Path(line.split('=>',1)[1].strip().split()[0]).resolve()) for line in l.stdout.decode().splitlines() if '=>' in line and line.split('=>',1)[1].strip().startswith('/')}
 for p,h in originals.items():assert sha(Path(p))==h
 r['passed']=True
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
