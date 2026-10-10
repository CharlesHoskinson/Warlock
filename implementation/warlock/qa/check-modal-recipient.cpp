// Exercise the real private selector with isolated native-object substitutes.
// This is algorithm evidence, not owning ABI/native input evidence.
#include <memory>
#include <vector>
#include <iostream>
#include <stdexcept>
struct Window;
using PHLWINDOW=std::shared_ptr<Window>;
struct Workspace { bool visible=true; bool isVisible() const{return visible;} };
struct Rule { bool flag=false; bool valueOrDefault() const{return flag;} };
struct Rules { Rule focus; const Rule& noFocus() const{return focus;} };
struct Dialog {bool modal=true;};
struct Toplevel {std::shared_ptr<Dialog> m_dialog;};
struct Surface {std::shared_ptr<Toplevel> m_toplevel;};
struct Window {
 bool mapped=true,hidden=false,minimized=false,blocked=false,modal=false;
 std::shared_ptr<Workspace> m_workspace;
 std::weak_ptr<int> m_monitor;
 std::shared_ptr<Surface> m_xdgSurface;
 std::shared_ptr<Rules> m_ruleApplicator=std::make_shared<Rules>();
 PHLWINDOW owner;
 PHLWINDOW parent() const{return owner;}
 bool isHidden() const{return hidden;}
 bool isInputBlocked() const{return blocked;}
 bool acceptsInput() const{return !minimized&&!hidden&&!blocked;}
 bool isModal() const{return modal;}
};
namespace Desktop {
 namespace WindowPolicy {inline bool isMinimized(const PHLWINDOW& w){return w->minimized;}}
 namespace View {inline bool validMapped(const PHLWINDOW& w){return w&&w->mapped;}}
 struct State {std::vector<PHLWINDOW> order;const auto& windows() const{return order;}};
 inline State state;
 inline State* windowState(){return &state;}
}
#include "ModalRecipient.hpp"
int main(){
 auto ws=std::make_shared<Workspace>();auto mon=std::make_shared<int>(0);
 auto node=[&](PHLWINDOW parent=nullptr,bool modal=false){auto w=std::make_shared<Window>();w->owner=parent;w->modal=modal;w->m_workspace=ws;w->m_monitor=mon;return w;};
 auto root=node(),modal=node(root,true),nested=node(modal,true),peer=node(),sibling=node(root,true);
 int checks=0,failures=0;
 auto selected=[&](PHLWINDOW expected,bool restoring=false,bool navigating=false){auto result=WarlockModal::focusRecipient(root,restoring,navigating);return result.has_value()&&*result==expected;};
 auto refused=[&](){return !WarlockModal::focusRecipient(root).has_value();};
 auto check=[&](const char* name,bool passed){std::cout<<name<<": "<<(passed?"pass":"FAIL")<<'\n';if(!passed)++failures;++checks;};
 try {
 Desktop::state.order={root,peer};check("eligible singleton root",selected(root));
 root->m_ruleApplicator->focus.flag=true;check("no-focus singleton refuses",refused());root->m_ruleApplicator->focus.flag=false;
 root->blocked=true;check("input-blocked singleton refuses",refused());root->blocked=false;
 Desktop::state.order={root,modal,peer};check("eligible modal",selected(modal));
 modal->blocked=true;check("blocked modal never falls back to parent",refused());modal->blocked=false;
 modal->m_ruleApplicator->focus.flag=true;check("no-focus modal refuses",refused());modal->m_ruleApplicator->focus.flag=false;
 Desktop::state.order={root,modal,nested,peer};check("eligible deepest modal",selected(nested));
 nested->blocked=true;check("blocked deepest never falls back to ancestor",refused());nested->blocked=false;
 nested->m_ruleApplicator->focus.flag=true;check("no-focus deepest refuses",refused());nested->m_ruleApplicator->focus.flag=false;
 Desktop::state.order={root,modal,sibling,peer};sibling->blocked=true;check("blocked sibling does not erase ambiguity",refused());sibling->blocked=false;
 Desktop::state.order={root,modal,peer};modal->mapped=false;check("retired modal releases parent",selected(root));modal->mapped=true;
 modal->minimized=true;root->minimized=true;check("restore resolves minimized modal",selected(modal,true));modal->minimized=false;root->minimized=false;
 check("unrelated eligible root ignores foreign modal",WarlockModal::focusRecipient(peer)==std::optional<PHLWINDOW>(peer));
 root->owner=modal;check("cyclic ancestry refuses",refused());root->owner=nullptr;
 std::cout<<"checks="<<checks<<", failures="<<failures<<'\n';return failures?1:0;
 }catch(const std::exception& error){std::cerr<<error.what()<<'\n';root->owner=nullptr;return 1;}
}
