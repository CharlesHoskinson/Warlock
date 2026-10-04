#include <functional>
#include <iostream>
#include <cstdlib>
#include <memory>
#include <vector>
struct Compositor { bool m_isShuttingDown=false; };
static Compositor compositor;
static Compositor* g_pCompositor=&compositor;
struct EventLoop {
    std::vector<std::function<void()>> tasks;
    void doLater(std::function<void()> fn) { tasks.push_back(fn); }
    void one() { if(tasks.empty()) return;auto fn=tasks.front();tasks.erase(tasks.begin());fn(); }
};
static EventLoop loop;
static EventLoop* g_pEventLoopManager=&loop;
namespace Config {
struct CMonitorRuleManager {
    bool m_reloadScheduled=false;
    int applications=0;
    std::function<void()> duringApply;
    void scheduleReload();
    void ensureMonitorStatus() {
        // PRODUCTION_CONSUME
        ++applications;
        if(duringApply) { auto fn=std::move(duringApply);duringApply={};fn(); }
    }
    void render() { // PRODUCTION_RENDER
    }
};
static std::unique_ptr<CMonitorRuleManager> singleton;
static std::unique_ptr<CMonitorRuleManager>& monitorRuleMgr() { return singleton; }
}
using namespace Config;
// PRODUCTION_SCHEDULE
static int checks=0;
static void check(bool value) { if(!value) { std::cerr<<"failed "<<checks+1<<'\n';std::exit(1); }++checks; }
int main() {
    singleton=std::make_unique<CMonitorRuleManager>(); auto& m=*singleton;
    m.scheduleReload();m.scheduleReload();m.scheduleReload();check(loop.tasks.size()==1);
    loop.one();check(m.applications==1 && !m.m_reloadScheduled && loop.tasks.empty());
    m.scheduleReload();m.render();check(m.applications==2 && !m.m_reloadScheduled);
    loop.one();check(m.applications==2);
    m.duringApply=[&]{m.scheduleReload();m.scheduleReload();};m.scheduleReload();loop.one();
    check(m.applications==3 && m.m_reloadScheduled && loop.tasks.size()==1);
    loop.one();check(m.applications==4 && !m.m_reloadScheduled);
    m.duringApply=[&]{m.scheduleReload();};m.scheduleReload();m.render();
    check(m.applications==5 && m.m_reloadScheduled && loop.tasks.size()==2);
    loop.one();loop.one();check(m.applications==6 && !m.m_reloadScheduled);
    m.scheduleReload();compositor.m_isShuttingDown=true;loop.one();check(m.applications==6);
    compositor.m_isShuttingDown=false;m.render();check(m.applications==7);
    g_pEventLoopManager=nullptr;m.scheduleReload();check(m.m_reloadScheduled && loop.tasks.empty());
    m.render();check(m.applications==8 && !m.m_reloadScheduled);g_pEventLoopManager=&loop;
    m.scheduleReload();g_pCompositor=nullptr;loop.one();check(m.applications==8);g_pCompositor=&compositor;
    m.render();check(m.applications==9);
    std::cout<<"checks: "<<checks<<'\n';
}
