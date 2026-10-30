// Component regressions. These are not compositor observations.
#include "../native/effect_cancellation_parser.hpp"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
using namespace warlock::cancellation;
struct Counts { int retired{}, mutations{}; Key last{}; bool failFormat{}; std::array<int,70> byPeer{}; };
static Counts counts;
static bool format(Buffer& b,const Key&,U id,U deadline,Phase phase,Facts facts) noexcept {
    if(counts.failFormat)return false;
    int n=std::snprintf(b.data.data(),b.data.size(),"%llu/%llu/%d/%llu/%llu/%d",
      (unsigned long long)id,(unsigned long long)deadline,(int)phase,
      (unsigned long long)facts.revision,(unsigned long long)facts.outputGeneration,(int)facts.reason);
    if(n<0 || static_cast<std::size_t>(n)>=b.data.size())return false;
    b.size=static_cast<std::size_t>(n);return true;
}
static void retire(void* c,const Key& k) noexcept {auto& n=*static_cast<Counts*>(c);++n.retired;n.last=k;if(k.owner.peer<n.byPeer.size())++n.byPeer[k.owner.peer];}
static ExecutionResult commit(void* c,const Owner::CommitPermit&) noexcept {
    ++static_cast<Counts*>(c)->mutations;
    return {Decision::CommittedObserved,Progress::NativeMutationStarted,{71,19,Reason::Applied}};
}
static ExecutionResult uncertain(void* c,const Owner::CommitPermit&) noexcept {
    ++static_cast<Counts*>(c)->mutations;
    return {Decision::ExecutionUncertain,Progress::NativeMutationStarted,{72,20,Reason::Unproven}};
}
static Key key(U peer,U request,U generation) {return {{peer,100+peer,1,peer,3},1,{request,generation,4,1,3,5,6,Intent::Operation::Restore}};}
static bool same(const Buffer& a,const Buffer& b){return a.size==b.size && !std::memcmp(a.data.data(),b.data.data(),a.size);}
static JsonObject* object(const char* text,JsonParser*& parser) {
    parser=json_parser_new();GError* error=nullptr;
    assert(json_parser_load_from_data(parser,text,-1,&error)); assert(!error);
    return json_node_get_object(json_parser_get_root(parser));
}

static unsigned checks=0;
static void check(bool value,const char* name) {++checks;if(!value)throw std::runtime_error(name);}
static ExecutionResult commitThenFormatFails(void* c,const Owner::CommitPermit& permit) noexcept {
    auto result=commit(c,permit);counts.failFormat=true;return result;
}
static ExecutionResult compensationThenFormatFails(void* c,const Owner::CommitPermit&) noexcept {
    ++static_cast<Counts*>(c)->mutations;counts.failFormat=true;
    return {Decision::RefusedAfterProvedCompensation,Progress::NativeMutationStarted,{73,21,Reason::NativeRefusal,"native-refusal"}};
}
static void regressions() {
    const auto a=key(1,1,1),peerKey=key(2,1,1);
    {
        counts={};Owner o(format,retire,&counts);auto first=o.prepare(a,100,10,0,0);U id=first.record->id;
        auto sibling=o.prepare(peerKey,100,10,0,0);U siblingId=sibling.record->id;
        counts.failFormat=true;auto cancelled=o.cancel(a,id,100,{9,10,Reason::Unproven});
        check(cancelled.error==Error::Resource && cancelled.record && cancelled.record->phase==Phase::Cancelled,"cancel semantic fence precedes failed formatting");
        check(!cancelled.record->replyReady && counts.retired==1 && counts.byPeer[1]==1 && counts.byPeer[2]==0,"cancel retires exact owner once despite format failure");
        auto later=o.commit(a,id,100,20,{},commit,&counts);
        check(later.record && later.record->phase==Phase::Cancelled && counts.mutations==0,"later commit cannot reopen failed-format cancellation");
        Record retained{};check(o.acknowledge(a,id,100,retained).error==Error::Unacknowledgeable,"incomplete terminal wire cannot be acknowledged");
        counts.failFormat=false;auto read=o.lookup(a,id,100);
        check(read.record && read.record->replyReady && read.record->phase==Phase::Cancelled && read.record->facts.revision==9,"read only encoding retry retains original cancelled facts");
        check(o.lookup(peerKey,siblingId,100).record->phase==Phase::Prepared && counts.byPeer[2]==0,"peer prepared resource remains untouched");
        check(o.cancel(a,id,100,{}).record->phase==Phase::Cancelled && counts.retired==1,"duplicate cancel does not retire twice");
        check(o.acknowledge(a,id,100,retained).record && retained.facts.revision==9,"ack transfers exact completed terminal record");
    }
    {
        counts={};Owner o(format,retire,&counts);auto p=o.prepare(a,100,10,0,0);U id=p.record->id;
        Buffer fallback{};check(format(fallback,a,id,100,Phase::ExecutionUnknown,{}),"uncertainty fallback control is complete before mutation");
        auto result=o.commit(a,id,100,20,{},commitThenFormatFails,&counts);
        check(result.error==Error::None && result.record->phase==Phase::ExecutionUnknown && result.record->replyReady && result.record->hasProof && result.record->proofPhase==Phase::Committed,"post-execution format failure retains complete Unknown and typed committed proof separately");
        check(same(result.record->reply,fallback) && result.record->facts.reason==Reason::Unproven,"preinstalled complete Unknown wire remains byte-identical while terminal encoding fails");
        Record retained{};check(o.acknowledge(a,id,100,retained).error==Error::Unacknowledgeable,"pending terminal serialization cannot acknowledge Unknown fallback");
        check(counts.mutations==1 && counts.retired==1,"committed mutation and token retirement happen once");
        check(o.cancel(a,id,100,{}).record->phase==Phase::ExecutionUnknown && result.record->hasProof && counts.mutations==1,"late cancel cannot replace committed proof or reopen execution while formatting fails");
        check(o.commit(a,id,100,21,{},commit,&counts).record->phase==Phase::ExecutionUnknown && counts.mutations==1,"pending serialization never executes again");
        counts.failFormat=false;auto read=o.lookup(a,id,100);
        check(read.record && read.record->replyReady && read.record->phase==Phase::Committed && !read.record->hasProof && read.record->facts.revision==71 && read.record->facts.outputGeneration==19,"completed terminal cache uses actual observed facts after encoding retry");
        check(o.acknowledge(a,id,100,retained).record && retained.phase==Phase::Committed,"only complete encoded terminal transfers through acknowledgement");
    }
    {
        counts={};Owner o(format,retire,&counts);auto p=o.prepare(a,100,10,0,0);U id=p.record->id;
        counts.failFormat=true;auto expired=o.commit(a,id,100,100,{},commit,&counts);
        check(expired.record && expired.record->phase==Phase::Refused && counts.mutations==0 && counts.retired==1,"expiry fences execution before failed encoding");
        counts.failFormat=false;check(o.commit(a,id,100,20,{},commit,&counts).record->phase==Phase::Refused && counts.mutations==0,"clock rollback cannot reopen terminal expiry");
    }
    {
        counts={};Owner o(format,retire,&counts);auto p=o.prepare(a,100,10,0,0);U id=p.record->id;
        check(o.commit(a,id,100,20,{},nullptr,&counts).error==Error::Invalid && p.record->phase==Phase::Prepared,"null execution callback rejected before boundary");
        auto wrong=a;wrong.intent.revision++;
        check(o.cancel(wrong,id,100,{}).error==Error::Foreign && counts.retired==0,"wrong full context cannot cancel resource");
        check(o.cancel(a,id+1,100,{}).error==Error::Foreign && counts.retired==0,"wrong prepared identity cannot cancel resource");
        check(o.cancel(a,id,101,{}).error==Error::Foreign && counts.retired==0,"wrong deadline cannot cancel resource");
    }
    {
        counts={};Owner o(format,retire,&counts);std::array<U,64> ids{};
        for(U i=1;i<=64;++i){auto p=o.prepare(key(i,1,1),100,10,0,0);check(p.record && p.error==Error::None,"all sixty-four distinct owner slots admitted");ids[i-1]=p.record->id;}
        check(o.prepare(key(65,1,1),100,10,0,0).error==Error::Capacity,"global capacity refuses a free sixty-fifth owner");
        auto seventh=key(7,1,1);o.cancel(seventh,ids[6],100,{});
        check(o.prepare(key(65,1,1),100,10,0,0).error==Error::Capacity,"terminal unacknowledged slot still consumes global capacity");
        Record retained{};check(o.acknowledge(seventh,ids[6],100,retained).record!=nullptr,"exact terminal acknowledgement frees one slot");
        auto replacement=o.prepare(key(65,1,1),100,10,0,0);check(replacement.record && replacement.record->id>ids[63],"capacity reuse preserves monotonic native identity");
        check(counts.retired==1 && counts.byPeer[7]==1 && counts.byPeer[8]==0,"capacity turnover retires only acknowledged generation token");
    }
    {
        counts={};Owner o(format,retire,&counts);auto p=o.prepare(a,100,10,0,0);U id=p.record->id;
        auto result=o.commit(a,id,100,20,{},compensationThenFormatFails,&counts);
        check(result.record && result.error==Error::None && result.record->phase==Phase::ExecutionUnknown && result.record->replyReady && result.record->hasProof && result.record->proofPhase==Phase::Refused,"proved compensated refusal keeps complete Unknown until serialization succeeds");
        check(o.cancel(a,id,100,{}).record->phase==Phase::ExecutionUnknown && counts.mutations==1 && counts.retired==1,"compensated progress is never relabeled cancelled and never repeated");
        counts.failFormat=false;auto terminal=o.lookup(a,id,100);
        check(terminal.record->phase==Phase::Refused && terminal.record->facts.revision==73 && terminal.record->facts.outputGeneration==21 && !terminal.record->hasProof,"encoded compensated refusal retains actual typed proof facts");
    }
    {
        counts={};Owner o(format,retire,&counts);auto p=o.prepare(a,100,10,0,0);U id=p.record->id;counts.failFormat=true;
        check(o.commit(a,id,100,20,{},commit,&counts).error==Error::Resource && p.record->phase==Phase::Prepared && counts.mutations==0 && counts.retired==0,"failed fallback reservation refuses before mutation boundary");
        o.cancel(a,id,100,{});check(p.record->phase==Phase::Cancelled && counts.mutations==0 && counts.retired==1,"cancellation still fences execution after failed fallback reservation");
    }
    const std::string good=R"({"protocolVersion":3,"kind":"effect-prepare","binding":{"lifetime":"1","session":"1","frontend":"3"},"effectProtocol":1,"cancellationProtocol":1,"intent":{"request":"1","generation":"1","incarnation":"4","operation":"restore","context":{"lifetime":"1","epoch":"3","output":"5","revision":"6"}},"deadlineMonotonicNs":"100"})";
    check(parseWire(good,1,101).has_value(),"actual raw parser accepts exact full request");
    auto changed=good;changed.insert(1,"\"protocolVersion\":3,");check(!parseWire(changed,1,101),"raw duplicate outer member refused");
    changed=good;auto pos=changed.find("\"revision\":\"6\"");changed.insert(pos,"\"revision\":\"6\",");check(!parseWire(changed,1,101),"raw duplicate nested member refused");
    changed=good;pos=changed.find("\"request\":\"1\"");changed.replace(pos,13,"\"request\":\"1\\u0000junk\"");check(!parseWire(changed,1,101),"decoded embedded NUL refused before C string truncation");
    changed=good;changed.insert(2,1,'\0');check(!parseWire(changed,1,101),"raw NUL byte refused");
    check(!parseWire(std::string(8193,' '),1,101),"oversized raw request refused before parse");
    check(!boundedWire("[[[[[0]]]]]"),"excess raw nesting refused before parse");
    check(!parseWire(good,0,101),"missing authenticated peer identity refused");
}

int main(){try {
    regressions();counts={};
    Owner o(format,retire,&counts);auto a=key(1,1,1),b=key(2,1,1);
    auto p=o.prepare(a,100,10,0,0);assert(p.record);U id=p.record->id;
    Buffer prepared=p.record->reply;assert(same(o.prepare(a,100,11,0,0).record->reply,prepared));
    assert(o.prepare(key(1,2,2),100,11,0,0).error==Error::Busy);
    assert(o.lookup(b,id,100).error==Error::Foreign);
    auto c=o.cancel(a,id,100,{7,8,Reason::Unproven});assert(c.record && c.record->phase==Phase::Cancelled);
    Buffer cancelled=c.record->reply;assert(counts.retired==1 && counts.last==a && counts.mutations==0);
    assert(same(o.commit(a,id,100,20,{},commit,&counts).record->reply,cancelled));
    assert(same(o.cancel(a,id,100,{}).record->reply,cancelled));
    Record journal{};assert(o.acknowledge(a,id,100,journal).record && same(journal.reply,cancelled));
    assert(o.prepare(a,100,20,1,1).error==Error::Expired);
    auto q=o.prepare(key(1,2,2),100,20,1,1);assert(q.record);
    auto committed=o.commit(q.record->key,q.record->id,100,20,{},commit,&counts);
    assert(committed.record && committed.record->phase==Phase::Committed && counts.mutations==1);
    Buffer receipt=committed.record->reply;auto k2=committed.record->key;U id2=committed.record->id;
    assert(same(o.cancel(k2,id2,100,{}).record->reply,receipt));
    assert(o.acknowledge(k2,id2,100,journal).record);
    auto u=o.prepare(key(1,3,3),100,20,2,2);assert(u.record);auto ku=u.record->key;U uid=u.record->id;
    assert(o.commit(ku,uid,100,20,{},uncertain,&counts).record->phase==Phase::ExecutionUnknown);
    assert(o.cancel(ku,uid,100,{}).record->phase==Phase::ExecutionUnknown);
    assert(o.acknowledge(ku,uid,100,journal).error==Error::Unacknowledgeable);
    auto peer=o.prepare(b,100,20,0,0);assert(peer.record);assert(o.busy(b.owner));
    o.retireOwner(a.owner);assert(o.busy(a.owner) && o.busy(b.owner));
    auto expire=o.commit(b,peer.record->id,100,100,{},commit,&counts);assert(expire.record->phase==Phase::Refused && counts.mutations==2);
    JsonParser* parser=nullptr;
    const char* good=R"({"kind":"effect-prepare","intent":{"context":{"revision":"6","output":"5","epoch":"3","lifetime":"1"},"operation":"restore","incarnation":"4","generation":"1","request":"1"},"binding":{"frontend":"3","session":"1","lifetime":"1"},"deadlineMonotonicNs":"100","effectProtocol":1,"cancellationProtocol":1,"protocolVersion":3})";
    auto* obj=object(good,parser);auto parsed=parse(obj,1,101);assert(parsed && parsed->key==a && parsed->deadline==100);g_object_unref(parser);
    const char* extra=R"({"protocolVersion":3,"kind":"effect-cancellation-negotiate","binding":{"lifetime":"1","session":"1","frontend":"3"},"requestId":"1","cancellationProtocol":1,"extra":1})";
    obj=object(extra,parser);assert(!parse(obj,1,101));g_object_unref(parser);
    const char* bad=R"({"protocolVersion":3,"kind":"effect-cancellation-negotiate","binding":{"lifetime":"1","session":"1","frontend":"3"},"requestId":"01","cancellationProtocol":1})";
    obj=object(bad,parser);assert(!parse(obj,1,101));g_object_unref(parser);
    std::printf("{\"passed\":true,\"additionalChecks\":%u}\n",checks);
    return 0;
} catch(const std::exception& e) {std::fprintf(stderr,"FAIL: %s\n",e.what());return 1;}
}
