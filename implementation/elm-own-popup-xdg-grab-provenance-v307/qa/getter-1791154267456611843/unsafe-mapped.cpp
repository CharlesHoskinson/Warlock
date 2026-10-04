
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
std::optional<SXDGActiveGrabSnapshot> CXDGShellProtocol::currentActiveGrab() const {
    if (!g_pSeatManager || !m_grab || g_pSeatManager->m_seatGrab != m_grab ||
        m_grabbed.empty() || m_grabbed.size() > 64 || m_popups.size() > 512)
        return std::nullopt;
    const auto owner = m_grabOwner.lock();
    if (!owner)
        return std::nullopt;
    SXDGActiveGrabSnapshot snapshot{m_grab, owner, {}};
    snapshot.popups.reserve(m_grabbed.size());
    size_t ownerMatches = 0;
    for (const auto& weak : m_grabbed) {
        const auto popup = weak.lock();
        if (!popup || std::ranges::find(m_popups, popup) == m_popups.end() ||
            std::ranges::find(snapshot.popups, popup) != snapshot.popups.end() || !popup->good())
            return std::nullopt;
        const auto xdg = popup->m_surface.lock();
        const auto surface = xdg ? xdg->m_surface.lock() : nullptr;
        if (!xdg || false || xdg->m_popup.lock() != popup || !surface ||
            !surface->getResource() || !surface->getResource()->resource() || !m_grab->accepts(surface))
            return std::nullopt;
        if (popup == owner)
            ++ownerMatches;
        snapshot.popups.push_back(popup);
    }
    if (ownerMatches != 1 || g_pSeatManager->m_seatGrab != snapshot.grab)
        return std::nullopt;
    return snapshot;
}

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
