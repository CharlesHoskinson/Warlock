#include "native-candidate/PinLifetime.hpp"
#include "native-candidate/PinJson.hpp"
#include <memory>
#include <iostream>
#include <stdexcept>
#include <limits>
struct Window {int id;};
int main(){
 int count=0;auto check=[&](bool value){++count;if(!value)throw std::runtime_error("CPU lifetime/codec check "+std::to_string(count));};
 using Strong=std::shared_ptr<Window>;using Weak=std::weak_ptr<Window>;PinLifetime<Strong,Weak>r;
 auto a=std::make_shared<Window>(1),b=std::make_shared<Window>(2);
 const auto first=r.query(a,true,true);check(first==1);check(r.query(a,true,false)==first);check(r.opened(a,true)==first);
 const auto peer=r.query(b,true,true);check(peer==2);r.closed(a);check(r.query(a,true,true)==0);check(r.query(a,true,false)==0);check(r.query(b,true,false)==peer);
 check(r.query(a,false,true)==0);const auto opened=r.opened(a,true);check(opened>peer&&opened!=first);check(r.query(a,true,true)==opened);check(r.opened(a,true)==opened);
 r.closed(a);r.closed(a);check(r.query(a,true,true)==0);check(r.opened(a,false)==0);check(r.query(a,true,true)==0);check(r.opened(a,true)>opened);
 auto missing=std::make_shared<Window>(3);check(r.query(missing,true,false)==0);r.closed(missing);check(r.query(missing,true,true)==0);check(r.opened(missing,true)>opened);
 alignas(Window)unsigned char memory[sizeof(Window)];auto old=Strong(new(memory)Window{4},[](Window*p){p->~Window();});auto generation=r.query(old,true,true);r.closed(old);old.reset();auto reused=Strong(new(memory)Window{5},[](Window*p){p->~Window();});check(r.query(reused,true,false)==0);check(r.query(reused,true,true)>generation);check(r.query(b,true,false)==peer);
 PinLifetime<Strong,Weak>exhausted(std::numeric_limits<uint64_t>::max());check(exhausted.query(a,true,true)==0);check(exhausted.opened(a,true)==0);check(r.query({},true,true)==0);
 PinJson token={{"pid",1},{"generation",std::string("18446744073709551615")},{"text",std::string("quote\"\n\0end",11)}};
 check(token==token);check(!(PinJson(true)==PinJson(1)));check(!(PinJson("1")==PinJson(1)));check(PinJson(nullptr).dump()=="null");check(token.at("generation").get<std::string>()=="18446744073709551615");check(token.at("text").get<std::string>().size()==11);
 PinJson nested={{"ok",true},{"backend",{{"message","failed"},{"code","x"}}}};check(nested.at("ok").get<bool>());check(nested.at("backend").at("message").get<std::string>()=="failed");
 bool refused=false;try{PinJson(1).get<bool>();}catch(const std::runtime_error&){refused=true;}check(refused);refused=false;try{token.at("missing");}catch(const std::out_of_range&){refused=true;}check(refused);
 PinJson array(std::vector<PinJson>{token,nested});check(array.dump().front()=='[');auto copied=token;token["pid"]=2;check(copied==token);check(!(PinJson::object()==PinJson(nullptr)));
 std::cout<<"{\"cpuChecks\":"<<count<<",\"nativeExecuted\":false}\n";
}
