"""Compile actual accessor body against typed lifetime stubs; no compositor claim."""
import hashlib,json,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('getter-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
p=ROOT/'candidate/src/protocols/XDGShell.cpp';body=p.read_text().split('std::optional<SXDGActiveGrabSnapshot> CXDGShellProtocol::currentActiveGrab() const {',1)[1];body='std::optional<SXDGActiveGrabSnapshot> CXDGShellProtocol::currentActiveGrab() const {'+body
stub=r'''
#include <algorithm>
#include <cassert>
#include <memory>
#include <optional>
#include <vector>
#include <iostream>
template<class T> using SP=std::shared_ptr<T>;
template<class T> using WP=std::weak_ptr<T>;
struct Resource { bool alive=true;void* resource(){return alive?this:nullptr;} };
struct Surface { SP<Resource> r=std::make_shared<Resource>();SP<Resource> getResource(){return r;} };
struct Popup;
struct XDG {WP<Surface> m_surface;WP<Popup> m_popup;bool m_mapped=true;};
struct Popup {WP<XDG> m_surface;WP<XDG> m_parent;bool valid=true;bool good(){return valid;}};
struct Grab {std::vector<SP<Surface>> surfs;bool accepts(SP<Surface> s){return std::ranges::find(surfs,s)!=surfs.end();}};
struct Seat {SP<Grab> m_seatGrab;};
SP<Seat> g_pSeatManager;
struct SXDGActiveGrabSnapshot{SP<Grab> grab;SP<Popup> owner;std::vector<SP<Popup>> popups;};
struct CXDGShellProtocol {SP<Grab> m_grab;WP<Popup> m_grabOwner;std::vector<WP<Popup>> m_grabbed;std::vector<SP<Popup>> m_popups;std::optional<SXDGActiveGrabSnapshot> currentActiveGrab() const;};
struct Fixture {CXDGShellProtocol p;SP<Surface> s=std::make_shared<Surface>();SP<XDG> x=std::make_shared<XDG>();SP<Popup> o=std::make_shared<Popup>();Fixture(){g_pSeatManager=std::make_shared<Seat>();p.m_grab=std::make_shared<Grab>();g_pSeatManager->m_seatGrab=p.m_grab;x->m_surface=s;x->m_popup=o;o->m_surface=x;p.m_grab->surfs={s};p.m_grabOwner=o;p.m_grabbed={o};p.m_popups={o};}};
'''
main=r'''
int main(){int n=0;auto check=[&](bool b){assert(b);++n;};
{Fixture f;auto s=f.p.currentActiveGrab();check(s&&s->owner==f.o&&s->grab==f.p.m_grab&&s->popups==f.p.m_popups);check(f.o->m_parent.expired());check(g_pSeatManager->m_seatGrab==f.p.m_grab);}
{Fixture f;g_pSeatManager.reset();check(!f.p.currentActiveGrab());}
{Fixture f;g_pSeatManager->m_seatGrab=std::make_shared<Grab>();check(!f.p.currentActiveGrab());}
{Fixture f;f.p.m_grab.reset();check(!f.p.currentActiveGrab());}
{Fixture f;f.p.m_grabbed.clear();check(!f.p.currentActiveGrab());}
{Fixture f;f.p.m_grabbed.resize(65,f.o);check(!f.p.currentActiveGrab());}
{Fixture f;f.p.m_popups.resize(513,f.o);check(!f.p.currentActiveGrab());}
{Fixture f;f.p.m_grabOwner.reset();check(!f.p.currentActiveGrab());}
{Fixture f;f.p.m_grabbed.push_back({});check(!f.p.currentActiveGrab());}
{Fixture f;f.p.m_popups.clear();check(!f.p.currentActiveGrab());}
{Fixture f;f.p.m_grabbed.push_back(f.o);check(!f.p.currentActiveGrab());}
{Fixture f;f.o->valid=false;check(!f.p.currentActiveGrab());}
{Fixture f;f.o->m_surface.reset();check(!f.p.currentActiveGrab());}
{Fixture f;f.x->m_mapped=false;check(!f.p.currentActiveGrab());}
{Fixture f;f.x->m_popup.reset();check(!f.p.currentActiveGrab());}
{Fixture f;f.x->m_surface.reset();check(!f.p.currentActiveGrab());}
{Fixture f;f.s->r.reset();check(!f.p.currentActiveGrab());}
{Fixture f;f.s->r->alive=false;check(!f.p.currentActiveGrab());}
{Fixture f;f.p.m_grab->surfs.clear();check(!f.p.currentActiveGrab());}
{Fixture f;auto stranger=std::make_shared<Popup>();f.p.m_grabOwner=stranger;check(!f.p.currentActiveGrab());}
// Deliberately does not establish whole-grab exclusivity: census owner must reject this extra.
{Fixture f;f.p.m_grab->surfs.push_back(std::make_shared<Surface>());check(bool(f.p.currentActiveGrab()));}
std::cout<<n<<" witnesses\n";}
'''
r={'passed':False,'nativeAcceptance':False,'scope':'Actual getter body extraction with typed mock lifetime/resource/grab dependencies; whole-grab census/authenticated host still external','source':str(p),'sourceSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'controls':[]}
try:
 for name,b in [('production',body),('unsafe-active-grab',body.replace('g_pSeatManager->m_seatGrab != m_grab','false').replace('g_pSeatManager->m_seatGrab != snapshot.grab','false')),('unsafe-mapped',body.replace('!xdg->m_mapped','false')),('unsafe-membership',body.replace('!m_grab->accepts(surface)','false'))]:
  cpp=OUT/(name+'.cpp');cpp.write_text(stub+b+main);binary=OUT/name;c=subprocess.run(['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-MD','-MF',str(OUT/(name+'.d')),str(cpp),'-o',str(binary)],capture_output=True,timeout=30);(OUT/(name+'.compile.stderr')).write_bytes(c.stderr);assert c.returncode==0,c.stderr.decode()
  q=subprocess.run([str(binary)],capture_output=True,timeout=3);(OUT/(name+'.stdout')).write_bytes(q.stdout);(OUT/(name+'.stderr')).write_bytes(q.stderr);r['controls'].append({'name':name,'exitCode':q.returncode,'sourceSHA256':hashlib.sha256(cpp.read_bytes()).hexdigest()});assert (q.returncode==0)==(name=='production')
 r['tools']={'/usr/bin/c++':hashlib.sha256(Path('/usr/bin/c++').resolve().read_bytes()).hexdigest()}
 r['artifacts']={str(x.relative_to(OUT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in OUT.iterdir() if x.is_file()}
 r['passed']=True
except Exception as e:r['error']=repr(e)
finally:(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS' if r['passed'] else r['error'])
if not r['passed']:raise SystemExit(1)
