from pathlib import Path
p=Path(__file__).parent/'producer/CommitLedger.hpp'
s=p.read_text()
s=s.replace('struct Frame {', '''struct Source {
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
struct Frame {''')
s=s.replace('bool endpoint=false;\n};','bool endpoint=false;\n    std::vector<MemberFrame> members;\n};',1)
s=s.replace('bool active=false,promoted=false,suspended=false;', 'bool active=false,promoted=false,suspended=false;\n    std::vector<Source> sources;\n    std::map<std::string,std::vector<Rect>> sceneFrom;\n    std::string sceneOperation;')
s=s.replace('if(!found->second.swapped)return Result::Rejected;', '''if(!found->second.swapped)return Result::Rejected;
        if(!sources.empty()){
            if(frame.members.size()!=sources.size())return Result::Rejected;
            for(size_t i=0;i<sources.size();++i)if(frame.members[i].source!=sources[i])return Result::Rejected;
        }''')
s=s.replace('origins.clear();active=true;suspended=false;', 'origins.clear();sources.clear();sceneFrom.clear();active=true;suspended=false;')
s=s.replace('    bool retarget(const Identity& identity', '''    void seedFamily(std::vector<Source> captured,std::string token,std::string hash,std::string operation){
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
    std::optional<Frame> prepareFamily(std::string output,uint64_t generation,double progress,uint64_t now){
        auto members=sceneRectangles(output,progress);if(members.empty())return {};
        auto frame=prepare(output,generation,bounds(members),progress,progress==1,now);if(!frame)return {};
        frame->members=std::move(members);pending.at(frame->sequence).frame=*frame;return frame;
    }
    const auto& familySources()const{return sources;}
    bool retarget(const Identity& identity''')
p.write_text(s)
