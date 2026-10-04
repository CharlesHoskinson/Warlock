#include <memory>
#include <cstdio>
#include <utility>
struct Size { int x,y; bool operator==(const Size&) const = default; };
struct Mode { Size pixelSize; };
struct Params { bool success; unsigned format; };
struct Buffer { Size size; Params params; Params dmabuf() const {return params;} };
struct State { bool enabled=true; std::shared_ptr<Buffer> buffer; std::shared_ptr<Mode> mode,customMode; };
struct OutputState {
    State value;
    const State& state() const {return value;}
    void setBuffer(std::shared_ptr<Buffer> buffer) {value.buffer=buffer;}
};
struct Swapchain {
    unsigned selections=0,rollbacks=0;
    std::shared_ptr<Buffer> candidate;
    std::shared_ptr<Buffer> next(void*) {selections++;return candidate;}
    void rollback() {rollbacks++;}
};
struct Output { std::shared_ptr<OutputState> state=std::make_shared<OutputState>(); std::shared_ptr<Swapchain> swapchain=std::make_shared<Swapchain>(); };
struct Owner { std::shared_ptr<Output> m_output=std::make_shared<Output>();unsigned m_drmFormat=42; };
namespace Log {enum Level {TRACE,DEBUG};struct Logger {template<class... T> void log(Level,const char*,T&&...) {}}; inline Logger object;inline Logger* logger=&object;}
struct CMonitorState { std::shared_ptr<Owner> m_owner=std::make_shared<Owner>();void ensureBufferPresent(); };
// ACTUAL_PRODUCTION_FUNCTION

#define CHECK(name,condition) do {if(!(condition)){std::fprintf(stderr,"FAIL: %s\n",name);return 1;}std::puts(name);checks++;} while(0)
int main() {
    unsigned checks=0;
    CMonitorState monitor;
    auto& output=*monitor.m_owner->m_output;
    auto& state=output.state->value;
    auto fresh=std::make_shared<Buffer>(Buffer{{800,600},{true,42}});
    output.swapchain->candidate=fresh;
    state.mode=std::make_shared<Mode>(Mode{{800,600}});
    auto exact=std::make_shared<Buffer>(Buffer{{800,600},{true,42}});
    state.buffer=exact;monitor.ensureBufferPresent();
    CHECK("exact size and format reused",state.buffer==exact && output.swapchain->selections==0);
    state.buffer=std::make_shared<Buffer>(Buffer{{960,640},{true,42}});monitor.ensureBufferPresent();
    CHECK("old scaled 960x640 replaced for restored 800x600",state.buffer==fresh && output.swapchain->selections==1 && output.swapchain->rollbacks==1);
    state.buffer=std::make_shared<Buffer>(Buffer{{800,640},{true,42}});monitor.ensureBufferPresent();
    CHECK("height-only mismatch replaced",state.buffer==fresh && output.swapchain->selections==2);
    state.buffer=std::make_shared<Buffer>(Buffer{{960,600},{true,42}});monitor.ensureBufferPresent();
    CHECK("width-only mismatch replaced",state.buffer==fresh && output.swapchain->selections==3);
    state.buffer=std::make_shared<Buffer>(Buffer{{800,600},{true,99}});monitor.ensureBufferPresent();
    CHECK("matching size wrong format replaced",state.buffer==fresh && output.swapchain->selections==4);
    state.buffer=std::make_shared<Buffer>(Buffer{{800,600},{false,42}});monitor.ensureBufferPresent();
    CHECK("unusable dmabuf replaced",state.buffer==fresh && output.swapchain->selections==5);
    state.buffer.reset();monitor.ensureBufferPresent();
    CHECK("missing buffer selected",state.buffer==fresh && output.swapchain->selections==6);
    state.enabled=false;auto retired=std::make_shared<Buffer>(Buffer{{960,640},{true,42}});state.buffer=retired;monitor.ensureBufferPresent();
    CHECK("disabled output unchanged",state.buffer==retired && output.swapchain->selections==6);
    state.enabled=true;state.mode.reset();state.customMode=std::make_shared<Mode>(Mode{{800,600}});state.buffer=exact;monitor.ensureBufferPresent();
    CHECK("custom-mode exact buffer reused",state.buffer==exact && output.swapchain->selections==6);
    state.buffer=retired;monitor.ensureBufferPresent();
    CHECK("custom-mode stale buffer replaced",state.buffer==fresh && output.swapchain->selections==7);
    state.mode=std::make_shared<Mode>(Mode{{960,640}});output.swapchain->candidate=retired;state.buffer=retired;monitor.ensureBufferPresent();
    CHECK("selected mode takes precedence over custom mode",state.buffer==retired && output.swapchain->selections==7);
    CHECK("replacement does not advance swapchain counter",output.swapchain->rollbacks==output.swapchain->selections);
    std::printf("checks: %u\n",checks);return 0;
}
