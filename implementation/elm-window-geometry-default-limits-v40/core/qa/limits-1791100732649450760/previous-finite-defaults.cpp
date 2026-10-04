
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <limits>
#include <memory>
#include <optional>
struct Vector2D {double x=0,y=0;Vector2D()=default;Vector2D(double a,double b):x(a),y(b){};Vector2D clamp(Vector2D low)const{return {std::max(x,low.x),std::max(y,low.y)};}bool operator==(const Vector2D&)const=default;};
struct Box {Vector2D xy;Vector2D pos()const{return xy;}};
struct Owner {struct {Box geometry;} m_current;};
struct CXDGToplevelResource {std::shared_ptr<Owner>m_owner;Vector2D layoutMinSize();Vector2D layoutMaxSize();
    struct {
        Vector2D minSize = {1337420, 694200};
        Vector2D maxSize = {1337420, 694200};
    } m_pending, m_current;
};
struct Property {std::optional<Vector2D>value_;bool hasValue(){return value_.has_value();}Vector2D value(){return *value_;}};
struct Boolean {bool v=false;bool valueOrDefault(){return v;}};
struct Rules {Property low,high;Boolean noMax;Property&minSize(){return low;}Property&maxSize(){return high;}Boolean&noMaxSize(){return noMax;}};
struct Xdg {std::shared_ptr<CXDGToplevelResource>m_toplevel;};
struct Hints {int min_width=0,min_height=0,max_width=0,max_height=0;};
struct Xwayland {std::shared_ptr<Hints>m_sizeHints=std::make_shared<Hints>();};
struct CWindow {std::shared_ptr<Rules>m_ruleApplicator=std::make_shared<Rules>();std::shared_ptr<Xdg>m_xdgSurface=std::make_shared<Xdg>();std::shared_ptr<Xwayland>m_xwaylandSurface=std::make_shared<Xwayland>();bool m_isX11=false;std::optional<Vector2D>minSize();std::optional<Vector2D>maxSize();};
#define UNLIKELY(x) (x)
struct Surface {struct {bool texture=false,buffer=false;}m_current,m_pending;void map(){}void unmap(){}};
struct Resource {void error(int,const char*){}};
struct Event {void emit(){}};
struct Commit {struct {int v=0;}m_current,m_pending;std::shared_ptr<CXDGToplevelResource>m_toplevel;std::shared_ptr<Surface>m_surface=std::make_shared<Surface>();std::shared_ptr<Resource>m_resource=std::make_shared<Resource>();bool m_initialCommit=false,m_mapped=false;struct {Event map,unmap,commit;}m_events;void run();};

Vector2D CXDGToplevelResource::layoutMinSize() {
    Vector2D minSize;
    if (m_current.minSize.x > 1)
        minSize.x = m_owner ? m_current.minSize.x + m_owner->m_current.geometry.pos().x : m_current.minSize.x;
    if (m_current.minSize.y > 1)
        minSize.y = m_owner ? m_current.minSize.y + m_owner->m_current.geometry.pos().y : m_current.minSize.y;
    return minSize;
}
Vector2D CXDGToplevelResource::layoutMaxSize() {
    Vector2D maxSize;
    if (m_current.maxSize.x > 1)
        maxSize.x = m_owner ? m_current.maxSize.x + m_owner->m_current.geometry.pos().x : m_current.maxSize.x;
    if (m_current.maxSize.y > 1)
        maxSize.y = m_owner ? m_current.maxSize.y + m_owner->m_current.geometry.pos().y : m_current.maxSize.y;
    return maxSize;
}
std::optional<Vector2D> CWindow::minSize() {
    // first check for overrides
    if (m_ruleApplicator->minSize().hasValue())
        return m_ruleApplicator->minSize().value();

    // then check if we have any proto overrides
    bool hasSizeHints = m_xwaylandSurface ? !!m_xwaylandSurface->m_sizeHints : false;
    bool hasTopLevel  = m_xdgSurface ? !!m_xdgSurface->m_toplevel : false;
    if ((m_isX11 && !hasSizeHints) || (!m_isX11 && !hasTopLevel))
        return std::nullopt;

    Vector2D minSize = m_isX11 ? Vector2D(m_xwaylandSurface->m_sizeHints->min_width, m_xwaylandSurface->m_sizeHints->min_height) : m_xdgSurface->m_toplevel->layoutMinSize();

    minSize = minSize.clamp({1, 1});

    return minSize;
}
std::optional<Vector2D> CWindow::maxSize() {
    // first check for overrides
    if (m_ruleApplicator->maxSize().hasValue())
        return m_ruleApplicator->maxSize().value();

    // then check if we have any proto overrides
    if (((m_isX11 && !m_xwaylandSurface->m_sizeHints) || (!m_isX11 && (!m_xdgSurface || !m_xdgSurface->m_toplevel)) || m_ruleApplicator->noMaxSize().valueOrDefault()))
        return std::nullopt;

    constexpr const double NO_MAX_SIZE_LIMIT = std::numeric_limits<double>::max();

    Vector2D maxSize = m_isX11 ? Vector2D(m_xwaylandSurface->m_sizeHints->max_width, m_xwaylandSurface->m_sizeHints->max_height) : m_xdgSurface->m_toplevel->layoutMaxSize();

    if (maxSize.x < 5)
        maxSize.x = NO_MAX_SIZE_LIMIT;
    if (maxSize.y < 5)
        maxSize.y = NO_MAX_SIZE_LIMIT;

    return maxSize;
}
void Commit::run(){

        m_current = m_pending;
        if (m_toplevel)
            m_toplevel->m_current = m_toplevel->m_pending;

        if UNLIKELY (m_initialCommit && m_surface->m_pending.buffer) {
            m_resource->error(-1, "Buffer attached before initial commit");
            return;
        }

        if (m_surface->m_current.texture && !m_mapped) {
            // Mapping does not imply maximization. Decoration negotiation and
            // fullscreen-controller state own their respective client facts.
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

int main(){unsigned checks=0;auto verify=[&](bool v,const char*n){++checks;if(!v)std::fprintf(stderr,"FAIL %s\n",n);return v;};constexpr double unlimited=std::numeric_limits<double>::max();
 auto top=std::make_shared<CXDGToplevelResource>();CWindow window;window.m_xdgSurface->m_toplevel=top;Commit commit;commit.m_toplevel=top;
 if(!verify(top->m_pending.minSize==Vector2D{0,0}&&top->m_pending.maxSize==Vector2D{0,0}&&top->m_current.minSize==Vector2D{0,0}&&top->m_current.maxSize==Vector2D{0,0},"never-set protocol defaults unspecified"))return 1;
 if(!verify(window.minSize()==Vector2D{1,1}&&window.maxSize()==Vector2D{unlimited,unlimited},"never-set normalized limits"))return 1;
 for(Vector2D minimum: {Vector2D{0,0},Vector2D{60,0},Vector2D{0,70},Vector2D{60,70}})for(Vector2D maximum:{Vector2D{0,0},Vector2D{600,0},Vector2D{0,700},Vector2D{600,700}}){
  auto oldMin=top->m_current.minSize,oldMax=top->m_current.maxSize;top->m_pending.minSize=minimum;top->m_pending.maxSize=maximum;
  if(!verify(top->m_current.minSize==oldMin&&top->m_current.maxSize==oldMax,"pending does not change committed hints"))return 1;
  commit.run();
  if(!verify(top->m_current.minSize==minimum&&top->m_current.maxSize==maximum,"actual surface commit applies hints"))return 1;
  auto expectedMin=Vector2D{minimum.x>1?minimum.x:0,minimum.y>1?minimum.y:0};auto expectedMax=Vector2D{maximum.x>1?maximum.x:0,maximum.y>1?maximum.y:0};
  if(!verify(top->layoutMinSize()==expectedMin&&top->layoutMaxSize()==expectedMax,"independent unspecified axes and explicit limits preserved"))return 1;
  if(!verify(window.minSize()==Vector2D{std::max(1.,expectedMin.x),std::max(1.,expectedMin.y)}&&window.maxSize()==Vector2D{expectedMax.x<5?unlimited:expectedMax.x,expectedMax.y<5?unlimited:expectedMax.y},"Window per-axis unspecified normalization"))return 1;
 }
 top->m_pending.minSize={120,80};top->m_pending.maxSize={120,80};commit.run();
 if(!verify(window.minSize()==Vector2D{120,80}&&window.maxSize()==Vector2D{120,80},"explicit fixed-size hints preserved"))return 1;
 top->m_pending.minSize={0,0};top->m_pending.maxSize={0,0};commit.run();
 if(!verify(window.minSize()==Vector2D{1,1}&&window.maxSize()==Vector2D{unlimited,unlimited},"explicit zero reset equals never-set"))return 1;
 top->m_owner=std::make_shared<Owner>();top->m_owner->m_current.geometry.xy={3,4};top->m_pending.minSize={60,0};top->m_pending.maxSize={600,0};commit.run();
 if(!verify(top->layoutMinSize()==Vector2D{63,0}&&top->layoutMaxSize()==Vector2D{603,0},"existing explicit geometry-offset policy retained"))return 1;
 window.m_ruleApplicator->low.value_=Vector2D{90,95};window.m_ruleApplicator->high.value_=Vector2D{800,805};
 if(!verify(window.minSize()==Vector2D{90,95}&&window.maxSize()==Vector2D{800,805},"window rule overrides retained"))return 1;
 window.m_ruleApplicator->high.value_.reset();window.m_ruleApplicator->noMax.v=true;
 if(!verify(!window.maxSize(),"no-max-size rule retained"))return 1;
 std::printf("checks %u\n",checks);return 0;
}
