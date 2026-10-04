
#include <hyprutils/math/Vector2D.hpp>
#include <cmath>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
using Hyprutils::Math::Vector2D;
template<class T> struct Rule { std::optional<T> v; bool hasValue() const {return v.has_value();} T value() const {return v.value();} T valueOrDefault() const {return v.value_or(T{});} };
struct Rules {Rule<Vector2D> minimum,maximum; Rule<bool> disabled; auto minSize(){return minimum;} auto maxSize(){return maximum;} auto noMaxSize(){return disabled;}};
// Already converted protocol observations are stub inputs; conversion is tested
// separately in V162. These methods themselves are verbatim owning source.
struct Top {Vector2D minimum{},maximum{}; Vector2D layoutMinSize(){return minimum;} Vector2D layoutMaxSize(){return maximum;}};
struct Xdg {std::shared_ptr<Top> m_toplevel=std::make_shared<Top>();};
struct Hints {int min_width=0,min_height=0,max_width=0,max_height=0;};
struct Xwayland {std::shared_ptr<Hints> m_sizeHints=std::make_shared<Hints>();};
struct CWindow {
 bool m_isX11=false;
 std::shared_ptr<Rules> m_ruleApplicator=std::make_shared<Rules>();
 std::shared_ptr<Xdg> m_xdgSurface=std::make_shared<Xdg>();
 std::shared_ptr<Xwayland> m_xwaylandSurface=std::make_shared<Xwayland>();
 std::optional<Vector2D> minSize(); std::optional<Vector2D> maxSize();
};

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

int main(){
 int checks=0;
 auto check=[&](const char* name,bool value){std::cout<<name<<" "<<value<<"\n";if(!value)throw std::runtime_error(name);++checks;};
 const double unlimited=std::numeric_limits<double>::max();
 CWindow w;
 check("absent-protocol-min-clamped-to-one",w.minSize()==std::optional<Vector2D>{{1,1}});
 check("zero-protocol-max-normalized-unlimited",w.maxSize()==std::optional<Vector2D>{{unlimited,unlimited}});
 w.m_xdgSurface->m_toplevel->minimum={108,42};
 check("GTK-minimum-preserved",w.minSize()==std::optional<Vector2D>{{108,42}});
 w.m_ruleApplicator->minimum.v=Vector2D{130,64};
 check("minimum-rule-overrides-protocol",w.minSize()==std::optional<Vector2D>{{130,64}});
 w.m_ruleApplicator->minimum.v=Vector2D{-8,2};
 check("invalid-rule-minimum-not-validated-by-core",w.minSize()==std::optional<Vector2D>{{-8,2}});
 w.m_ruleApplicator->minimum.v.reset();
 w.m_xdgSurface->m_toplevel->maximum={1,4};
 check("positive-tiny-max-lost-to-layout-sentinel",w.maxSize()==std::optional<Vector2D>{{unlimited,unlimited}});
 w.m_xdgSurface->m_toplevel->maximum={5,100};
 check("five-is-finite-boundary",w.maxSize()==std::optional<Vector2D>{{5,100}});
 w.m_ruleApplicator->maximum.v=Vector2D{900,700};
 w.m_xdgSurface->m_toplevel->maximum={400,300};
 check("rule-can-widen-protocol-maximum",w.maxSize()==std::optional<Vector2D>{{900,700}});
 w.m_ruleApplicator->maximum.v=Vector2D{3,4};
 check("tiny-rule-maximum-bypasses-normalization",w.maxSize()==std::optional<Vector2D>{{3,4}});
 w.m_ruleApplicator->maximum.v=Vector2D{std::numeric_limits<double>::quiet_NaN(),4};
 check("nonfinite-rule-maximum-preserved",std::isnan(w.maxSize()->x));
 w.m_ruleApplicator->maximum.v.reset();w.m_ruleApplicator->disabled.v=true;
 check("noMaxSize-rule-suppresses-protocol-limit",!w.maxSize());
 w.m_ruleApplicator->disabled.v=false;w.m_xdgSurface->m_toplevel.reset();
 check("missing-toplevel-min-is-unavailable",!w.minSize());
 check("missing-toplevel-max-is-unavailable",!w.maxSize());
 std::cout<<"checks="<<checks<<"\n";
}
