#include "client_producer.hpp"
#include <array>
#include <iostream>
#include <string>
#include <vector>
using namespace preview;
using namespace preview::bridge;

static void receipt(const std::string& name, const std::string& detail) {
    Wire out; std::cout << out.text("name",name).boolean("passed",true).text("detail",detail).finish() << '\n';
}
static std::array<uint64_t,14> values(const Job& j) {
    return {j.binding.lifetime.value,j.binding.session.value,j.binding.frontend.value,
            j.context.lifetime.value,j.context.incarnation.value,j.context.output.value,
            j.context.privacy.value,j.context.rendering.value,j.context.scene.value,
            j.context.content.value,j.request.value,j.origin.value,j.clock.value,j.deadline};
}
static void exact(const Job& actual,const Job& expected,const std::string& label) {
    static const std::array<const char*,14> names={"binding.lifetime","binding.session","binding.frontend",
        "context.lifetime","context.incarnation","context.output","context.privacy","context.rendering",
        "context.scene","context.content","request","origin","clock","deadline"};
    auto a=values(actual), e=values(expected);
    for(size_t i=0;i<a.size();++i) {
        require(a[i]==e[i],"Native field differs from retained input");
        receipt(label+"."+names[i],std::to_string(a[i]));
    }
}
static void worker(const std::string& name,const std::string& text,const Job& expected,ClientCommand kind) {
    Json input(text); auto o=input.object(); Json::fields(o,{"kind","job"});
    require(std::string_view(Json::text(o,"kind"))==(kind==ClientCommand::Acquire?"acquire":"cancel"),"Actual command kind");
    auto job=decodeJob(Json::child(o,"job")); exact(job,expected,name+".decoded");
    const std::string identity="family:"+std::to_string(expected.context.incarnation.value);
    require(decodeClientCommand(identity,text,expected,{})==kind,"Actual client command");
    receipt(name+".client-command",identity);
    auto mismatch=expected; ++mismatch.deadline; bool rejected=false;
    try { (void)decodeClientCommand(identity,text,mismatch,{}); }
    catch(const std::exception& e) { rejected=std::string_view(e.what())=="Exact original native client job"; }
    require(rejected,"Mismatched expected job must refuse"); receipt(name+".mismatch","Exact original native client job");
    Wire emitted; auto json=emitted.job(job).finish(); Json roundtrip(json);
    exact(decodeJob(roundtrip.object()),expected,name+".reemitted");
    receipt(name+".wire-job",json);
}
int main(int argc,char** argv) { try {
    require(argc==4,"Expected two Acquire and one Cancel worker commands");
    const uint64_t high=9007199254740993ULL;
    const Binding binding{{high},{1},{1}};
    const Context context{{high},{high},{1},{1},{1},{1},{1}};
    const Job first{binding,context,{1},{1},{high},9007199254740993ULL};
    const Job second{binding,context,{1},{1},{high},9007199254740994ULL};
    worker("first-acquire",argv[1],first,ClientCommand::Acquire);
    worker("second-acquire",argv[2],second,ClientCommand::Acquire);
    worker("second-cancel",argv[3],second,ClientCommand::Cancel);
    const Binding distinctBinding{{9007199254741000ULL},{9007199254741001ULL},{9007199254741002ULL}};
    const Context distinctContext{{9007199254741000ULL},{9007199254741003ULL},{9007199254741004ULL},
        {9007199254741005ULL},{9007199254741006ULL},{9007199254741007ULL},{9007199254741008ULL}};
    for (unsigned i=0;i<2;++i) {
        const Job distinct{distinctBinding,distinctContext,{9007199254741009ULL},{9007199254741010ULL},
            {9007199254741011ULL},9007199254740993ULL+i};
        Wire out; auto encoded=out.job(distinct).finish(); Json parsed(encoded);
        auto label=std::string("distinct-")+std::to_string(i+1);
        exact(decodeJob(parsed.object()),distinct,label+".decoded");
        receipt(label+".wire-job",encoded);
    }
    const Job one{{{1},{1},{1}},{{1},{1},{1},{1},{1},{1},{1}},{1},{1},{1},1};
    Wire base; auto baseline=base.job(one).finish(); Json valid(baseline);
    exact(decodeJob(valid.object()),one,"numeric-baseline");
    receipt("numeric-baseline.wire-job",baseline);
    const std::vector<std::pair<const char*,const char*>> paths={
        {"binding","lifetime"},{"binding","session"},{"binding","frontend"},
        {"context","lifetime"},{"context","incarnation"},{"context","output"},
        {"context","privacy"},{"context","rendering"},{"context","scene"},{"context","content"},
        {"","request"},{"","origin"},{"","clock"},{"","deadline"}};
    for(const auto& [parent,field]:paths) {
        Json candidate(baseline); auto object=*parent?Json::child(candidate.object(),parent):candidate.object();
        json_object_set_int_member(object,field,1);
        auto bytes=json_to_string(json_parser_get_root(candidate.parser),FALSE);
        Json reparsed(bytes);
        bool rejected=false; try { (void)decodeJob(reparsed.object()); }
        catch(const std::exception& e) { rejected=std::string_view(e.what())=="Native string field"; }
        require(rejected,"Numeric field must fail native string type admission");
        std::string label="numeric."+std::string(*parent?std::string(parent)+".":"")+field;
        receipt(label,bytes);g_free(bytes);
    }
    return 0;
} catch(const std::exception& e) { std::cerr << e.what() << '\n'; return 1; } }
