"""Compile actual captured producer expressions with stub metadata accessors."""
import hashlib,json,re,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];UP=REPO/'implementation/elm-geometry-coordinate-authority-v406/qa/build-1791125085822287165';OUT=ROOT/'qa'/('characterization-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[];report={'passed':False,'nativeAcceptance':False,'dispatchAcceptance':False,'modelAcceptance':False,'scope':'Actual producer input/projection/sizePolicy expressions and actual402 private helper; stub metadata only, no native frame, protocol conversion or command execution','checks':checks,'commands':[]}
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def body(text,signature):
 start=text.index(signature);cursor=text.index('{',start)+1;depth=1
 while depth:
  depth+=(text[cursor]=='{')-(text[cursor]=='}');cursor+=1
 return text[start:cursor]
def run(name,args):
 p=subprocess.run(args,cwd=INPUT,capture_output=True,text=True,timeout=90);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr[-3500:];return p.stdout
try:
 build=json.loads((UP/'report.json').read_text());check('actual406 owning build passed',build['passed'] is True);report['upstreamReportSHA256']=sha(UP/'report.json');shutil.copy2(UP/'report.json',INPUT/'upstream-report.json')
 paths=['native/geometry-policy.inc','native/geometry.inc','candidate/ProspectiveGeometry.hpp','candidate/PlacementPolicy.hpp']
 report['owningInputs']={}
 for relative in paths:
  p=UP/'inputs'/relative;check('captured build input '+relative,sha(p)==build['artifacts']['inputs/'+relative]);target=INPUT/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);report['owningInputs'][relative]=sha(p)
 check('actual402 helper matches captured production',(INPUT/'candidate/ProspectiveGeometry.hpp').read_bytes()==(REPO/'implementation/elm-geometry-coordinate-policy-v402/candidate/ProspectiveGeometry.hpp').read_bytes())
 spec=REPO/'implementation/elm-geometry-coordinate-authority-v406/SPEC.md';shutil.copy2(spec,INPUT/'SPEC.md');report['specSHA256']=sha(spec);shutil.copy2(Path(__file__),INPUT/'test.py');report['testSourceSHA256']=sha(Path(__file__))
 geometry=(INPUT/'native/geometry.inc').read_text();policy=(INPUT/'native/geometry-policy.inc').read_text();serialization='\n\n'.join(body(geometry,s) for s in ['std::string geometryNumber(double value)','std::string geometryRect(const CBox& box)']);wire=next(line.strip() for line in geometry.splitlines() if line.strip().startswith('const auto sizePolicy=protocol==2'))
 (INPUT/'actual-number-rectangle.inc').write_text(serialization+'\n');(INPUT/'actual-size-policy-expression.inc').write_text(wire+'\n');report['extractedInputs']={'serialization':sha(INPUT/'actual-number-rectangle.inc'),'sizePolicy':sha(INPUT/'actual-size-policy-expression.inc')}
 prefix=r'''
#include <bit>
#include <charconv>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include "candidate/PlacementPolicy.hpp"
#include "candidate/ProspectiveGeometry.hpp"
using Hyprutils::Math::CBox;
using Hyprutils::Math::Vector2D;
using Hyprutils::Math::SBoxExtents;
struct Target {std::optional<Vector2D> minimum=Vector2D{108,42},maximum; auto minSize(){return minimum;}auto maxSize(){return maximum;}};
struct Raw {Vector2D minSize{108,42},maxSize{0,0};};
struct Top {Raw m_current;};
struct XdgCurrent {CBox geometry{0,0,320,180};};
struct Xdg {std::shared_ptr<Top> m_toplevel=std::make_shared<Top>();XdgCurrent m_current;};
struct Monitor {double m_scale=1;};
struct Space {CBox area{0,0,800,600};CBox workArea(bool){return area;}};
struct Workspace {std::shared_ptr<Space> m_space=std::make_shared<Space>();};
struct Window {
 std::shared_ptr<Target> target=std::make_shared<Target>();bool m_isX11=false;
 std::shared_ptr<Xdg> m_xdgSurface=std::make_shared<Xdg>();
 std::shared_ptr<Monitor> keepMonitor=std::make_shared<Monitor>();std::weak_ptr<Monitor> m_monitor=keepMonitor;
 std::shared_ptr<Workspace> m_workspace=std::make_shared<Workspace>();
 SBoxExtents reserved{Vector2D{0,24},Vector2D{0,0}};
 auto layoutTarget(){return target;}auto getFullWindowReservedArea(){return reserved;}
};
using PHLWINDOW=std::shared_ptr<Window>;
'''
 harness=r'''
std::string fragment(int protocol,const PHLWINDOW& window,const std::optional<GeometryProjection>& maximizeProjection,const std::optional<GeometryProjection>& restoreProjection){
'''+wire+r'''
 return "{"+(sizePolicy.empty()?std::string():sizePolicy.substr(1))+"}";
}
void emit(const char* name,const PHLWINDOW& window,int protocol=2){
 const std::optional<Elm::Placement::Original> original=Elm::Placement::Original{{120,130,320,180},{120,130,320,180}};
 const auto maximize=geometryProspective(window,true),restore=geometryProspective(window,false,original);
 std::cout<<"{\"case\":\""<<name<<"\",\"geometryInputAvailable\":"<<(geometryInput(window,Elm::ProspectiveGeometry::Operation::Maximize,CBox{0,0,1,1},{}).has_value()?"true":"false")<<",\"producerFragment\":"<<fragment(protocol,window,maximize,restore)<<"}\n";
}
int main(){
 auto w=std::make_shared<Window>();emit("GTK108x42-no-layout-maximum",w);emit("version1",w,1);
 w->target.reset();emit("unavailable-target",w);w=std::make_shared<Window>();w->m_xdgSurface->m_toplevel.reset();emit("unavailable-toplevel",w);
 w=std::make_shared<Window>();w->m_monitor.reset();emit("unavailable-monitor",w);
 w=std::make_shared<Window>();w->target->maximum=Vector2D{320,600};w->target->minimum=Vector2D{320,42};emit("fixed-layout-axis",w);
 w=std::make_shared<Window>();w->m_xdgSurface->m_toplevel->m_current.minSize={320,0};w->m_xdgSurface->m_toplevel->m_current.maxSize={320,0};emit("fixed-raw-axis",w);
 w=std::make_shared<Window>();w->m_xdgSurface->m_toplevel->m_current.maxSize={-1,0};emit("invalid-negative-raw",w);
 w=std::make_shared<Window>();w->target->maximum=Vector2D{std::numeric_limits<double>::quiet_NaN(),600.0};emit("invalid-nonfinite-layout",w);
 w=std::make_shared<Window>();w->m_xdgSurface->m_current.geometry.x=8;w->m_xdgSurface->m_current.geometry.y=9;emit("unsupported-nonzero-origin",w);
 w=std::make_shared<Window>();w->m_xdgSurface->m_toplevel->m_current.maxSize={400,300};w->target->maximum=Vector2D{900,700};emit("raw-maximum-widened-by-layout-rule",w);
 w=std::make_shared<Window>();w->keepMonitor->m_scale=2;emit("scale2-already-logical-input",w);
 w=std::make_shared<Window>();w->m_workspace.reset();emit("unavailable-workspace",w);
}
'''
 (INPUT/'characterization.cpp').write_text(prefix+'\n'+serialization+'\n'+policy+'\n'+harness);report['compiledSourceSHA256']=sha(INPUT/'characterization.cpp')
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','hyprutils'],text=True));run('compile',['c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(OUT/'dependencies.d'),'characterization.cpp','-o',str(OUT/'characterization'),*flags])
 output=run('producer-fragments',[str(OUT/'characterization')]);samples=[json.loads(line) for line in output.splitlines()];(OUT/'producer-fragments.json').write_text(json.dumps(samples,indent=2)+'\n');rows={x['case']:x for x in samples};check('13 actual producer cases',len(rows)==13)
 gtk=rows['GTK108x42-no-layout-maximum']['producerFragment']['sizePolicy'];check('GTK minimum/raw-unbounded actual input profile',gtk['inputs']['rawMinimum']==[108,42] and gtk['inputs']['rawMaximum']==[0,0] and gtk['inputs']['layoutMinimum']==[108,42] and gtk['inputs']['profile']=='wayland-zero-origin-v1');check('actual max reserved decoration projection',gtk['maximize']['logical']==[0,0,800,600] and gtk['maximize']['visual'] is None and gtk['maximize']['real']==[0,24,800,576] and gtk['maximize']['configure']==[800,576]);check('actual exact saved geometry restore projection',gtk['restoreGeometry']['real']==[120,130,320,180] and gtk['restoreGeometry']['configure']==[320,180])
 check('version1 emits no sizePolicy',rows['version1']['producerFragment']=={})
 for name in ['unavailable-target','unavailable-toplevel','unavailable-monitor','fixed-layout-axis','fixed-raw-axis','invalid-negative-raw','invalid-nonfinite-layout']:
  value=rows[name]['producerFragment'];check(name+' actual outer object contains null members',value=={'sizePolicy':{'inputs':None,'maximize':None,'restoreGeometry':None}})
 origin=rows['unsupported-nonzero-origin']['producerFragment']['sizePolicy'];check('nonzero-origin currently publishes zero-origin profile inputs while both projections refuse',origin['inputs']['profile']=='wayland-zero-origin-v1' and origin['inputs']['geometryOrigin']==[8,9] and origin['maximize'] is None and origin['restoreGeometry'] is None)
 narrow=rows['raw-maximum-widened-by-layout-rule']['producerFragment']['sizePolicy'];check('widened layout bound cannot override raw maximum',narrow['inputs']['rawMaximum']==[400,300] and narrow['inputs']['layoutMaximum']==[900,700] and narrow['maximize'] is None and narrow['restoreGeometry'] is not None)
 scaled=rows['scale2-already-logical-input']['producerFragment']['sizePolicy'];check('scale metadata differs without multiplying already-logical projection',scaled['inputs']['monitorScale']==2 and scaled['maximize']==gtk['maximize'])
 workspace=rows['unavailable-workspace']['producerFragment']['sizePolicy'];check('missing workspace retains input metadata but has no operation projection',workspace['inputs'] is not None and workspace['maximize'] is None and workspace['restoreGeometry'] is None)
 deps=shlex.split((OUT/'dependencies.d').read_text().replace('\\\n',' ').split(':',1)[1]);report['compilerDependencies']={str((INPUT/p).resolve()):sha((INPUT/p).resolve()) for p in deps}
 for path,digest in build['dependencies'].items():
  if '/hyprutils/math/' in path:check('owning exact Hyprutils header '+path,sha(path)==digest)
 linked=run('ldd',['ldd',str(OUT/'characterization')]);check('actual library closure resolves','not found' not in linked);libs={}
 for line in linked.splitlines():
  match=re.search(r'(?:=>\s+)?(/[^\s]+)\s+\(',line)
  if match:
   p=Path(match.group(1)).resolve(strict=True);libs[str(p)]=sha(p)
 library='/usr/lib/libhyprutils.so.0.14.2';check('actual owning406 Hyprutils library',library in libs and libs[library]==build['linkedLibraries'][library]);report['linkedLibraries']=libs
 report.update(passed=True,samples=len(samples),ambiguities=['SPEC says unavailable conversion has null outer sizePolicy; actual wire unconditionally emits object with null inputs/projections','Nonzero geometry origin is unsupported by402 project but actual406 inputs still advertise wayland-zero-origin-v1','Unavailable workspace retains profile inputs although operation projections are null'],limitations=['Stub Window/layout/XDG/workspace/monitor metadata only; no actual protocol conversion or rule resolver','SizePolicy fragment initializer only; full geometryFacts eligibility/capability/revision/envelope not exercised','No synthetic native frame, command dispatch, native ACK/pixel, model or release acceptance'])
 check('runner source remained unchanged',sha(Path(__file__))==report['testSourceSHA256'])
except Exception as error:report['passed']=False;report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
