// Synthetic devices/resources exercise verbatim production SeatManager methods.
// This is separate from full owning-TU compilation and actual native delivery.
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <memory>
#include <ranges>
#include <stdexcept>
#include <type_traits>
#include <vector>
template<class T> using SP=std::shared_ptr<T>;
template<class T> struct WP {
    std::weak_ptr<T> value;
    WP()=default;WP(const SP<T>& p):value(p){}
    WP& operator=(const SP<T>& p){value=p;return *this;}
    explicit operator bool()const{return !value.expired();}
    T* operator->()const{return value.lock().get();}
    SP<T> lock()const{return value.lock();}
    void reset(){value.reset();}
    bool expired()const{return value.expired();}
    bool operator==(const SP<T>& p)const{return value.lock()==p;}
};
struct Slot{std::function<void()> fn;bool active=true;};
struct Listener {
    SP<Slot> slot;
    Listener()=default;explicit Listener(SP<Slot> p):slot(std::move(p)){}
    Listener(Listener&& o)noexcept:slot(std::move(o.slot)){}
    Listener& operator=(Listener&& o)noexcept{reset();slot=std::move(o.slot);return *this;}
    ~Listener(){reset();}
    void reset(){if(slot)slot->active=false;slot.reset();}
};
struct Signal {
    std::vector<std::weak_ptr<Slot>> slots;unsigned count=0;std::function<void()> hook;
    Listener listen(std::function<void()> fn){auto p=std::make_shared<Slot>();p->fn=std::move(fn);slots.emplace_back(p);return Listener(p);}
    void emit(){count++;auto copy=slots;for(auto& w:copy)if(auto p=w.lock();p&&p->active)p->fn();auto fn=hook;if(fn)fn();}
};
struct CWLSurfaceResource {
    int owner;struct{Signal destroy;}m_events;
    explicit CWLSurfaceResource(int client):owner(client){}
    int client()const{return owner;}
};
struct wl_array{std::vector<uint32_t> items;};
static void wl_array_init(wl_array* p){p->items.clear();}
static void wl_array_release(wl_array* p){p->items.clear();}
static void* wl_array_add(wl_array* p,size_t n){p->items.resize(n/sizeof(uint32_t));return p->items.data();}
template<class T,class U>T sc(U v){return static_cast<T>(v);}
struct CScopeGuard{std::function<void()> fn;~CScopeGuard(){fn();}};
struct IKeyboard {
    bool m_active=false,m_enabled=true;int m_repeatRate=25,m_repeatDelay=600;
    struct{uint32_t depressed=0,latched=0,locked=0,group=0;}m_modifiersState;
    bool shareStates()const{return true;}bool isVirtual()const{return false;}
};
struct KeyboardResource {
    int owner;unsigned enters=0,leaves=0,mods=0;WP<CWLSurfaceResource> focus;std::vector<uint32_t> lastKeys;
    explicit KeyboardResource(int client):owner(client){}
    void sendMods(uint32_t,uint32_t,uint32_t,uint32_t){mods++;}
    void sendLeave(){if(focus)leaves++;focus.reset();}
    void sendEnter(SP<CWLSurfaceResource> surface,wl_array* keys){if(owner!=surface->client())throw std::runtime_error("foreign keyboard enter");enters++;focus=surface;lastKeys=keys->items;}
};
struct CWLSeatResource {
    int owner;std::vector<SP<KeyboardResource>>m_keyboards;
    explicit CWLSeatResource(int client):owner(client){}
    int client()const{return owner;}
};
struct InputManager {
    std::vector<SP<IKeyboard>>m_keyboards;std::vector<uint32_t>keys;
    const std::vector<uint32_t>& getKeysFromAllKBs()const{return keys;}
    bool shouldIgnoreVirtualKeyboard(SP<IKeyboard>)const{return false;}
};
static SP<InputManager>g_pInputManager=std::make_shared<InputManager>();
struct SeatProtocol {
    std::vector<SP<KeyboardResource>>m_keyboards;std::function<void()>keymapHook;
    void updateRepeatInfo(int,int){}
    void updateKeymap(){auto fn=keymapHook;if(fn)fn();}
};
struct CaptureProtocol{void updateKeymap(){}};
namespace PROTO{static SP<SeatProtocol>seat=std::make_shared<SeatProtocol>();static SP<CaptureProtocol>inputCapture=std::make_shared<CaptureProtocol>();}
namespace Log{static constexpr int ERR=1;struct Logger{void log(int,const char*){}};static SP<Logger>logger=std::make_shared<Logger>();}
class CSeatManager {
public:
    WP<IKeyboard>m_keyboard;
    struct{WP<CWLSurfaceResource>keyboardFocus;WP<CWLSeatResource>keyboardFocusResource;}m_state;
    struct{Listener keyboardSurfaceDestroy;}m_listeners;
    struct{Signal keyboardFocusChange;}m_events;
    struct Container{WP<CWLSeatResource>resource;};std::vector<SP<Container>>m_seatResources;
    void setKeyboard(SP<IKeyboard>);void setKeyboardFocus(SP<CWLSurfaceResource>);void updateActiveKeyboardData();
};
// PRODUCTION_METHODS
static unsigned checks;
#define CHECK(name,expression) do{checks++;if(!(expression)){std::cerr<<"failed "<<checks<<": "<<name<<"\n";return 1;}}while(0)
struct Fixture {
    CSeatManager manager;
    SP<CWLSurfaceResource>a=std::make_shared<CWLSurfaceResource>(1),b=std::make_shared<CWLSurfaceResource>(2);
    SP<IKeyboard>first=std::make_shared<IKeyboard>(),second=std::make_shared<IKeyboard>();
    SP<CWLSeatResource>seatA=std::make_shared<CWLSeatResource>(1),seatB=std::make_shared<CWLSeatResource>(2);
    SP<KeyboardResource>ka=std::make_shared<KeyboardResource>(1),kb=std::make_shared<KeyboardResource>(2);
    Fixture(){PROTO::seat=std::make_shared<SeatProtocol>();seatA->m_keyboards={ka};seatB->m_keyboards={kb};PROTO::seat->m_keyboards={ka,kb};g_pInputManager=std::make_shared<InputManager>();g_pInputManager->m_keyboards={first,second};for(auto s:{seatA,seatB}){auto c=std::make_shared<CSeatManager::Container>();c->resource=s;manager.m_seatResources.push_back(c);}}
};
int main(){
    {
        Fixture f;auto& m=f.manager;m.setKeyboardFocus(f.a);
        CHECK("admitted focus persists with no device",m.m_state.keyboardFocus==f.a);
        CHECK("absent device cannot invent resource or enter",m.m_state.keyboardFocusResource.expired()&&f.ka->enters==0&&f.kb->enters==0);
        CHECK("absent focus has destroy listener",bool(m.m_listeners.keyboardSurfaceDestroy.slot));
        auto count=m.m_events.keyboardFocusChange.count;m.setKeyboardFocus(f.a);
        CHECK("duplicate focus request is inert",m.m_events.keyboardFocusChange.count==count);
        m.setKeyboard(f.first);
        CHECK("first live keyboard enters current focus once",f.ka->enters==1&&f.kb->enters==0&&m.m_state.keyboardFocus==f.a);
        CHECK("current matching client owns keyboard resource",m.m_state.keyboardFocusResource==f.seatA);
        CHECK("restoration never invents held keys",f.ka->lastKeys.empty()&&g_pInputManager->keys.empty());
        CHECK("first keyboard becomes active",f.first->m_active);
        m.setKeyboard(f.first);CHECK("duplicate device cannot reenter",f.ka->enters==1);
        m.setKeyboard(f.second);CHECK("additional keyboard cannot steal or duplicate focus",f.ka->enters==1&&f.kb->enters==0&&m.m_state.keyboardFocus==f.a&&!f.first->m_active&&f.second->m_active);
        m.setKeyboard(nullptr);f.a->m_events.destroy.emit();m.setKeyboardFocus(f.b);
        CHECK("new popup focus records while keyboard absent",m.m_state.keyboardFocus==f.b&&f.kb->enters==0&&m.m_state.keyboardFocusResource.expired());
        m.setKeyboard(f.first);CHECK("restoration enters latest popup rather than prior window",f.kb->enters==1&&m.m_state.keyboardFocus==f.b&&m.m_state.keyboardFocusResource==f.seatB);
    }
    {
        Fixture f;f.manager.setKeyboardFocus(f.a);f.a->m_events.destroy.emit();
        CHECK("destroyed keyboardless surface clears intent",f.manager.m_state.keyboardFocus.expired()&&f.manager.m_state.keyboardFocusResource.expired());
        f.manager.setKeyboard(f.first);CHECK("retired popup cannot reenter",f.ka->enters==0&&f.kb->enters==0);
    }
    {
        Fixture f;f.manager.setKeyboardFocus(f.a);f.manager.setKeyboardFocus(nullptr);f.manager.setKeyboard(f.first);
        CHECK("null replacement cancels keyboardless intent",f.manager.m_state.keyboardFocus.expired()&&f.ka->enters==0);
    }
    {
        Fixture f;f.manager.setKeyboardFocus(f.a);f.manager.setKeyboardFocus(f.b);f.a->m_events.destroy.emit();
        CHECK("retired previous surface cannot clear latest request",f.manager.m_state.keyboardFocus==f.b);
        f.manager.setKeyboard(f.first);CHECK("only current client receives restore",f.ka->enters==0&&f.kb->enters==1);
    }
    {
        Fixture f;f.manager.m_seatResources.erase(f.manager.m_seatResources.begin());f.manager.setKeyboardFocus(f.a);f.manager.setKeyboard(f.first);
        CHECK("missing owning seat cannot enter foreign client",f.ka->enters==0&&f.kb->enters==0&&f.manager.m_state.keyboardFocusResource.expired());
    }
    {
        Fixture f;f.manager.setKeyboardFocus(f.a);PROTO::seat->keymapHook=[&]{PROTO::seat->keymapHook=nullptr;f.a->m_events.destroy.emit();};f.manager.setKeyboard(f.first);
        CHECK("keymap callback retirement cannot resurrect captured focus",f.manager.m_state.keyboardFocus.expired()&&f.ka->enters==0&&f.kb->enters==0);
    }
    {
        Fixture f;f.manager.setKeyboardFocus(f.a);PROTO::seat->keymapHook=[&]{PROTO::seat->keymapHook=nullptr;f.manager.setKeyboardFocus(f.b);};f.manager.setKeyboard(f.first);
        CHECK("keymap reentry preserves newer focus",f.manager.m_state.keyboardFocus==f.b&&f.ka->enters==0&&f.kb->enters==1);
    }
    {
        Fixture f;f.manager.setKeyboardFocus(f.a);PROTO::seat->keymapHook=[&]{PROTO::seat->keymapHook=nullptr;f.manager.setKeyboard(f.second);};f.manager.setKeyboard(f.first);
        CHECK("keymap reentry cannot restore obsolete keyboard",f.manager.m_keyboard==f.second&&f.ka->enters==0&&f.kb->enters==0&&!f.first->m_active&&f.second->m_active);
    }
    {
        Fixture f;f.manager.m_events.keyboardFocusChange.hook=[&]{f.manager.m_events.keyboardFocusChange.hook=nullptr;f.manager.setKeyboardFocus(f.b);};f.manager.setKeyboardFocus(f.a);f.a->m_events.destroy.emit();f.manager.setKeyboard(f.first);
        CHECK("focus signal reentry retains latest lifecycle listener",f.manager.m_state.keyboardFocus==f.b&&f.ka->enters==0&&f.kb->enters==1);
    }
    std::cout<<"actual-seat-method-checks: "<<checks<<"\n";return 0;
}
