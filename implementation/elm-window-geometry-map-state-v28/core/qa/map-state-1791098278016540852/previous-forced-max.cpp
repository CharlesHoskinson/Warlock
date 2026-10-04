
#include <cstdio>
#include <functional>
#include <memory>
#include <string>
#include <vector>
#define UNLIKELY(x) (x)
struct State {int value=0;};
struct SurfaceState {bool texture=false; bool buffer=false;};
struct Top {
    State m_current, m_pending;
    bool maximized=false;
    unsigned writes=0;
    void setMaximized(bool desired) {maximized=desired; ++writes;}
};
struct Surface {
    SurfaceState m_current, m_pending;
    unsigned maps=0, unmaps=0;
    void map(){++maps;}
    void unmap(){++unmaps;}
};
struct Resource {
    unsigned errors=0;
    void error(int, const char*) {++errors;}
};
struct Signal {
    unsigned count=0;
    std::function<void()> listener;
    void emit(){++count; if(listener) listener();}
};
struct Probe {
    State m_current, m_pending;
    std::shared_ptr<Top> m_toplevel=std::make_shared<Top>();
    std::shared_ptr<Surface> m_surface=std::make_shared<Surface>();
    std::shared_ptr<Resource> m_resource=std::make_shared<Resource>();
    bool m_initialCommit=false, m_mapped=false;
    struct {Signal map, unmap, commit;} m_events;
    void commit();
};

void Probe::commit(){

        m_current = m_pending;
        if (m_toplevel)
            m_toplevel->m_current = m_toplevel->m_pending;

        if UNLIKELY (m_initialCommit && m_surface->m_pending.buffer) {
            m_resource->error(-1, "Buffer attached before initial commit");
            return;
        }

        if (m_surface->m_current.texture && !m_mapped) {
            // this forces apps to not draw CSD.
            if (m_toplevel)
                m_toplevel->setMaximized(true);

            m_mapped = true;
            m_surface->map();
            m_events.map.emit();
            return;
        }

        if (!m_surface->m_current.texture && m_mapped) {
            m_mapped = false;
            m_events.unmap.emit();
            m_surface->unmap();
            return;
        }

        m_events.commit.emit();
        m_initialCommit = false;
    
}

int main() {
    unsigned checks=0;
    auto verify=[&](bool ok,const char*name){++checks; if(!ok)std::fprintf(stderr,"FAIL %s\n",name); return ok;};
    // Independent expected transitions: mapping changes lifetime facts, not MAX.
    for(bool texture:{false,true}) for(bool mapped:{false,true})
    for(bool initial:{false,true}) for(bool pendingBuffer:{false,true})
    for(bool hasTop:{false,true}) for(bool max:{false,true}) {
        Probe p; auto top=p.m_toplevel;
        if(!hasTop) p.m_toplevel.reset();
        p.m_pending.value=41; p.m_current.value=3;
        top->m_pending.value=43; top->m_current.value=5;
        top->maximized=max;
        p.m_surface->m_current.texture=texture;
        p.m_surface->m_pending.buffer=pendingBuffer;
        p.m_mapped=mapped; p.m_initialCommit=initial;
        p.commit();
        bool refused=initial&&pendingBuffer;
        bool maps=!refused&&texture&&!mapped;
        bool unmaps=!refused&&!texture&&mapped;
        bool ordinary=!refused&&!maps&&!unmaps;
        if(!verify(p.m_current.value==41 && top->m_current.value==(hasTop?43:5),"commit state copied"))return 1;
        if(!verify(top->maximized==max && top->writes==0,"mapping preserves exact configured MAX without setter"))return 1;
        if(!verify(p.m_resource->errors==unsigned(refused),"initial buffer refused"))return 1;
        if(!verify(p.m_mapped==(maps?true:unmaps?false:mapped),"map state transition"))return 1;
        if(!verify(p.m_surface->maps==unsigned(maps)&&p.m_events.map.count==unsigned(maps),"one map and signal"))return 1;
        if(!verify(p.m_surface->unmaps==unsigned(unmaps)&&p.m_events.unmap.count==unsigned(unmaps),"one unmap and signal"))return 1;
        if(!verify(p.m_events.commit.count==unsigned(ordinary)&&p.m_initialCommit==(ordinary?false:initial),"ordinary commit and initial flag preserved"))return 1;
    }
    // A real controller can configure either state from the map signal.
    for(bool initialMax:{false,true}) for(bool desired:{false,true}) {
        Probe p; p.m_surface->m_current.texture=true; p.m_toplevel->maximized=initialMax;
        p.m_events.map.listener=[&]{p.m_toplevel->setMaximized(desired);};
        p.commit();
        if(!verify(p.m_toplevel->maximized==desired&&p.m_toplevel->writes==1,"map listener owns requested MAX"))return 1;
    }
    Probe p; p.m_surface->m_current.texture=true; p.m_toplevel->maximized=true;
    p.commit(); p.m_surface->m_current.texture=false; p.commit();
    p.m_surface->m_current.texture=true; p.commit();
    if(!verify(p.m_surface->maps==2&&p.m_surface->unmaps==1&&p.m_toplevel->maximized&&p.m_toplevel->writes==0,"remap preserves configured MAX"))return 1;
    std::printf("checks %u\n",checks); return 0;
}
