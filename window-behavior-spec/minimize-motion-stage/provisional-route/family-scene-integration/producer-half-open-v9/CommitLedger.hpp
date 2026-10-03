#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <map>
#include <optional>
#include <regex>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

namespace OwnedRoute {
struct Identity {
    std::string stable;
    int64_t pid=0;
    bool operator==(const Identity&)const=default;
    bool valid()const{return pid>0 && std::regex_match(stable,std::regex("[0-9a-f]{1,16}"));}
};
struct Rect {
    double x=0,y=0,width=0,height=0;
    bool operator==(const Rect&)const=default;
    bool valid()const{return std::isfinite(x)&&std::isfinite(y)&&std::isfinite(width)&&std::isfinite(height)&&width>0&&height>0;}
};
inline bool validToken(const std::string& token) {
    return std::regex_match(token,std::regex("[0-9a-f]{12}-[1-9][0-9]{0,14}"));
}
inline bool validDigest(const std::string& digest) {
    return std::regex_match(digest,std::regex("[0-9a-f]{64}"));
}
struct Source {
    Identity identity;
    std::string digest;
    Rect nativeRect,atlasRect,iconRect;
    bool operator==(const Source&)const=default;
    bool valid()const{return identity.valid()&&validDigest(digest)&&nativeRect.valid()&&atlasRect.valid()&&iconRect.valid();}
};
struct MemberFrame {
    Source source;
    Rect rectangle;
    bool operator==(const MemberFrame&)const=default;
};
inline Rect mix(const Rect& a,const Rect& b,double p){return {a.x+(b.x-a.x)*p,a.y+(b.y-a.y)*p,a.width+(b.width-a.width)*p,a.height+(b.height-a.height)*p};}
inline Rect bounds(const std::vector<MemberFrame>& members){
    if(members.empty())throw std::invalid_argument("empty family frame");
    double x=members[0].rectangle.x,y=members[0].rectangle.y,right=x+members[0].rectangle.width,bottom=y+members[0].rectangle.height;
    for(const auto& m:members){x=std::min(x,m.rectangle.x);y=std::min(y,m.rectangle.y);right=std::max(right,m.rectangle.x+m.rectangle.width);bottom=std::max(bottom,m.rectangle.y+m.rectangle.height);}
    return {x,y,right-x,bottom-y};
}
struct Frame {
    uint64_t sequence=0,generation=0,submittedNs=0;
    std::string output,token,digest;
    Identity identity;
    Rect rectangle;
    double progress=0;
    bool endpoint=false;
    std::vector<MemberFrame> members;
    int bufferWidth=0,bufferHeight=0;
};
struct Presented {
    Frame frame;
    uint64_t timestampNs=0;
    uint64_t compositorSequence=0;
};
enum class Result {Rejected,Deferred,RecordedOld,RecordedCurrent};
class CommitLedger {
    struct Pending {Frame frame;bool swapped=false;std::optional<Presented> early;};
    std::map<uint64_t,Pending> pending;
    std::map<std::string,uint64_t> outputs,submitted,highwater,timewater,mscwater;
    std::map<std::string,Presented> origins;
    std::vector<Presented> history;
    std::set<std::string> ready,endReady;
    Identity currentIdentity;
    std::string currentToken,currentDigest;
    bool active=false,promoted=false,suspended=false;
    std::vector<Source> sources;
    std::map<std::string,std::vector<Rect>> sceneFrom;
    std::string sceneOperation;
    uint64_t nextSequence=0;
    Result accept(const Presented& p) {
        auto found=pending.find(p.frame.sequence);
        if(found==pending.end())return Result::Rejected;
        auto frame=found->second.frame;
        if(!found->second.swapped)return Result::Rejected;
        if(!sources.empty()){
            if(frame.members.size()!=sources.size())return Result::Rejected;
            for(size_t i=0;i<sources.size();++i)if(frame.members[i].source!=sources[i])return Result::Rejected;
        }
        if(!active || outputs[frame.output]!=frame.generation ||
            frame.identity!=currentIdentity || frame.digest!=currentDigest ||
            frame.sequence<=highwater[frame.output] || p.timestampNs<=timewater[frame.output] ||
            p.timestampNs<frame.submittedNs)return Result::Rejected;
        const auto priorMSC=mscwater[frame.output];
        if(p.compositorSequence && priorMSC && p.compositorSequence-priorMSC >= (uint64_t(1)<<63))return Result::Rejected;
        Presented actual{frame,p.timestampNs,p.compositorSequence};
        highwater[frame.output]=frame.sequence;timewater[frame.output]=p.timestampNs;
        if(p.compositorSequence)mscwater[frame.output]=p.compositorSequence;
        origins[frame.output]=actual;history.push_back(actual);
        if(history.size()>512)history.erase(history.begin());
        for(auto i=pending.begin();i!=pending.end();) {
            if(i->second.frame.output==frame.output && i->first<=frame.sequence)i=pending.erase(i);else ++i;
        }
        if(frame.token!=currentToken)return Result::RecordedOld;
        ready.insert(frame.output);
        if(frame.endpoint)endReady.insert(frame.output);else endReady.erase(frame.output);
        return Result::RecordedCurrent;
    }
public:
    void configure(std::map<std::string,uint64_t> generations) {
        if(generations.empty())throw std::invalid_argument("no required output");
        for(const auto& [name,generation]:generations)if(name.empty()||generation==0)throw std::invalid_argument("invalid output");
        cancel();
        auto retain=[&](auto& values){for(auto i=values.begin();i!=values.end();) {if(!generations.contains(i->first)||!outputs.contains(i->first)||generations.at(i->first)!=outputs.at(i->first))i=values.erase(i);else ++i;}};
        retain(submitted);retain(highwater);retain(timewater);retain(mscwater);
        outputs=std::move(generations);origins.clear();
    }
    void seed(Identity identity,std::string token,std::string digest) {
        if(outputs.empty() || !identity.valid() || !validToken(token) || !validDigest(digest))throw std::invalid_argument("invalid route identity/token/digest");
        cancel();currentIdentity=std::move(identity);currentToken=std::move(token);currentDigest=std::move(digest);
        origins.clear();sources.clear();sceneFrom.clear();active=true;suspended=false;
    }
    void seedFamily(std::vector<Source> captured,std::string token,std::string hash,std::string operation){
        if(captured.empty()||captured.size()>64||(operation!="minimize"&&operation!="restore"))throw std::invalid_argument("invalid family seed");
        std::set<std::string> ids;
        for(const auto& source:captured)if(!source.valid()||!ids.insert(source.identity.stable).second)throw std::invalid_argument("invalid/duplicate family source");
        seed(captured.front().identity,std::move(token),std::move(hash));sources=std::move(captured);sceneOperation=std::move(operation);
        for(const auto& [name,generation]:outputs){auto& from=sceneFrom[name];for(const auto& source:sources)from.push_back(sceneOperation=="minimize"?source.atlasRect:source.iconRect);}
    }
    bool familyMatches(const std::vector<Identity>& ids)const{
        if(ids.size()!=sources.size()||ids.empty())return false;
        for(size_t i=0;i<ids.size();++i)if(ids[i]!=sources[i].identity)return false;return true;
    }
    bool retargetFamily(const std::vector<Identity>& ids,const std::string& token,const std::string& operation){
        if(!familyMatches(ids)||(operation!="minimize"&&operation!="restore"))return false;
        for(const auto& [name,origin]:origins)if(origin.frame.members.size()!=sources.size())return false;
        if(!retarget(ids.front(),token))return false;
        sceneOperation=operation;sceneFrom.clear();
        for(const auto& [name,origin]:origins)for(const auto& member:origin.frame.members)sceneFrom[name].push_back(member.rectangle);
        return true;
    }
    bool promoteFamily(const std::vector<Identity>& ids,const std::string& token){return familyMatches(ids)&&promote(ids.front(),token);}
    std::vector<MemberFrame> sceneRectangles(const std::string& output,double progress)const{
        if(!active||sources.empty()||!sceneFrom.contains(output)||!std::isfinite(progress)||progress<0||progress>1)return {};
        std::vector<MemberFrame> result;const auto& from=sceneFrom.at(output);
        for(size_t i=0;i<sources.size();++i)result.push_back({sources[i],mix(from[i],sceneOperation=="minimize"?sources[i].iconRect:sources[i].atlasRect,progress)});
        return result;
    }
    std::optional<Frame> prepareFamily(std::string output,uint64_t generation,double progress,uint64_t now,int bufferWidth=0,int bufferHeight=0){
        if(bufferWidth<0||bufferHeight<0||bufferWidth>16384||bufferHeight>16384||(bufferWidth==0)!=(bufferHeight==0))return {};
        auto members=sceneRectangles(output,progress);if(members.empty())return {};
        auto frame=prepare(output,generation,bounds(members),progress,progress==1,now);if(!frame)return {};
        frame->members=std::move(members);frame->bufferWidth=bufferWidth;frame->bufferHeight=bufferHeight;pending.at(frame->sequence).frame=*frame;return frame;
    }
    const auto& familySources()const{return sources;}
    bool retarget(const Identity& identity,const std::string& token) {
        if(!active || identity!=currentIdentity || !validToken(token) ||
            token.substr(0,12)!=currentToken.substr(0,12) ||
            std::stoull(token.substr(13))<=std::stoull(currentToken.substr(13)) || !pending.empty())return false;
        if(origins.size()!=outputs.size())return false;
        currentToken=token;promoted=false;suspended=false;ready.clear();endReady.clear();return true;
    }
    bool promote(const Identity& identity,const std::string& token) {
        if(!active || suspended || identity!=currentIdentity || token!=currentToken)return false;
        promoted=true;return true;
    }
    void suspendAuthority(){promoted=false;suspended=true;}
    std::optional<Frame> prepare(std::string output,uint64_t generation,Rect rectangle,double progress,bool endpoint,uint64_t now) {
        if(!active || !outputs.contains(output) || outputs.at(output)!=generation || !rectangle.valid() ||
            !std::isfinite(progress) || progress<0 || progress>1 || (endpoint && progress!=1) || now==0 ||
            now<submitted[output] || pending.size()>=128)return {};
        Frame f{++nextSequence,generation,now,output,currentToken,currentDigest,currentIdentity,rectangle,progress,endpoint,{},0,0};
        pending.emplace(f.sequence,Pending{f,false,{}});submitted[output]=now;return f;
    }
    Result swapReturned(uint64_t sequence,bool succeeded) {
        auto i=pending.find(sequence);
        if(i==pending.end())return Result::Rejected;
        if(!succeeded){cancel();return Result::Rejected;}
        i->second.swapped=true;
        if(i->second.early)return accept(*i->second.early);
        return Result::Deferred;
    }
    Result present(uint64_t sequence,uint64_t timestamp,uint64_t compositorSequence) {
        auto i=pending.find(sequence);
        if(i==pending.end())return Result::Rejected;
        Presented p{i->second.frame,timestamp,compositorSequence};
        if(!i->second.swapped){if(i->second.early)return Result::Rejected;i->second.early=p;return Result::Deferred;}
        return accept(p);
    }
    void discarded(uint64_t sequence){if(pending.contains(sequence))cancel();}
    void outputRemoved(const std::string& name,uint64_t generation){if(outputs.contains(name)&&outputs.at(name)==generation)cancel();}
    bool timedOut(uint64_t now,uint64_t limit=2000000000ULL) {
        for(const auto& [sequence,p]:pending)if(now>p.frame.submittedNs && now-p.frame.submittedNs>limit){cancel();return true;}
        return false;
    }
    void cancel(){active=false;promoted=false;suspended=false;pending.clear();ready.clear();endReady.clear();}
    bool isActive()const{return active;}
    bool hasPending()const{return !pending.empty();}
    size_t pendingCount()const{return pending.size();}
    bool nativeReady()const{return active && promoted && ready.size()==outputs.size();}
    bool nativeEndpoint()const{return nativeReady() && endReady.size()==outputs.size();}
    const auto& presentedOrigins()const{return origins;}
    const auto& records()const{return history;}
    const std::string& token()const{return currentToken;}
};
}
