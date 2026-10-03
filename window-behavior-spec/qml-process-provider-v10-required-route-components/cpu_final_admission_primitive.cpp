// Explicit white-box production-fragment primitive; not actual Qt notification.
// All actor/kernel/source/closure fields here are assumed preconditions, not proof.
#include <array>
#include <algorithm>
#include <atomic>
#include <deque>
#include <map>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <vector>
#include <iostream>
struct Refused:std::runtime_error{using runtime_error::runtime_error;};
struct Row{struct Arm{void*process;}arm;struct Job{bool joined=true;};std::shared_ptr<Job>job=std::make_shared<Job>();unsigned lease=1;bool fault=false,current=true,kernel=true,accepted=true,normalLife=true,receipt=true,started=true,historical=true,exited=true,normal=true,out=true,err=true,gone=true;};
struct Primitive{
 int object=0;std::map<void*,std::shared_ptr<Row>>rows;std::vector<std::shared_ptr<Row>>history;std::mutex faultMutex;std::deque<std::pair<void*,unsigned>>queuedFaults;std::atomic_bool faultOverflow{false};struct Scope{std::array<void*,6>objects{};unsigned lease=1;}scope;std::shared_ptr<Row>r=std::make_shared<Row>();
 Primitive(){r->arm.process=&object;scope.objects[3]=&object;rows.emplace(&object,r);history.reserve(1);}
 void queue(unsigned lease){std::lock_guard admission(faultMutex);queuedFaults.emplace_back(&object,lease);}
 void commit(){auto bound=[&]{auto it=rows.find(scope.objects[3]);if(it==rows.end()||it->second!=r||r->lease!=scope.lease)throw Refused("Selected primitive tuple changed");};auto invalidate=[&]{r->fault=true;r->kernel=false;r->accepted=false;r->normalLife=false;};
 {
  std::lock_guard admission(faultMutex);bound();
  const bool matchedPending=std::any_of(queuedFaults.begin(),queuedFaults.end(),[&](const auto&fault){return fault.first==scope.objects[3]&&fault.second==scope.lease;});
  if(matchedPending||faultOverflow.load()||r->fault){invalidate();throw Refused("Matched pending fault/overflow forbids terminal retirement");}
  if(!r->job||!r->job->joined||!r->started||!r->historical||!r->exited||!r->normal||!r->out||!r->err||!r->gone)throw Refused("Terminal closure lost before admission commit");
  const auto selected=rows.find(r->arm.process);
  r->current=false;r->kernel=false;r->accepted=false;r->normalLife=true;r->receipt=true;history.push_back(r);rows.erase(selected);
 }
 }
};
int main(){try{unsigned checks=0;auto require=[&](bool ok){if(!ok)throw std::runtime_error("Exact final admission primitive failed");++checks;};
 {Primitive p;std::thread incoming([&]{p.queue(1);});incoming.join();bool refused=false;try{p.commit();}catch(const Refused&){refused=true;}require(refused&&p.rows.size()==1&&p.history.empty()&&p.r->fault&&!p.r->normalLife&&!p.r->accepted&&!p.r->kernel);}
 {Primitive p;p.faultOverflow=true;bool refused=false;try{p.commit();}catch(const Refused&){refused=true;}require(refused&&p.rows.size()==1&&p.history.empty()&&p.r->fault);}
 {Primitive p;std::thread old([&]{p.queue(0);});old.join();p.commit();require(p.rows.empty()&&p.history.size()==1&&p.r->normalLife&&!p.r->current&&!p.r->accepted&&!p.r->kernel);}
 {Primitive p;p.commit();std::thread late([&]{p.queue(1);});late.join();require(p.rows.empty()&&p.history.size()==1&&p.r->normalLife&&!p.r->fault);}
 std::cout<<"{\"result\":\"pass\",\"checks\":"<<checks<<",\"whiteBoxFinalAdmissionPrimitive\":true,\"actualRegistryFixture\":false,\"genuineQtSignalAtDisconnect\":false,\"actualActorClosureProved\":false}\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
