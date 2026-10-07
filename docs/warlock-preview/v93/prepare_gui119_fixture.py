"""Couple native visual channel to the original real persistent JSC fixture."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v119')
s=(root/'native/persistent-policy-lifetime-fixture-v2.cpp').read_text()
s=s.replace('#include "elm-preview-policy.h"','#include "elm-preview-policy.h"\n#include "preview-visual-channel.h"')
a=s.index('int main(')
s=s[:a]+'''struct ChannelCall {
    WarlockVisualChannel* channel;
    WarlockPreviewPolicy* policy;
    GObject* context;
    std::string op;
    const char* wire;
    char* output{};
    GError* error{};
    gboolean ok{};
};
static gpointer channel_call(gpointer raw) {
    auto& c=*static_cast<ChannelCall*>(raw);
    if(c.op=="attach")c.ok=warlock_visual_channel_attach(c.channel,c.policy,c.context,&c.output,&c.error);
    else if(c.op=="offer")c.ok=warlock_visual_channel_offer(c.channel,c.policy,c.context,&c.output,&c.error);
    else if(c.op=="retry")c.ok=warlock_visual_channel_retry(c.channel,c.policy,c.context,&c.output,&c.error);
    else if(c.op=="ack")c.ok=warlock_visual_channel_ack(c.channel,c.policy,c.context,c.wire,&c.error);
    else if(c.op=="current")c.ok=warlock_visual_channel_current(c.channel,c.policy,c.context,&c.error);
    else if(c.op=="invalidate")c.ok=warlock_visual_channel_invalidate(c.channel,c.context,&c.error);
    else if(c.op=="detach")c.ok=warlock_visual_channel_detach(c.channel,c.context,&c.error);
    else if(c.op=="close")c.ok=warlock_visual_channel_close(c.channel,&c.error);
    else std::abort();
    return nullptr;
}
static void finalized(gpointer target,GObject*) {*static_cast<GObject**>(target)=nullptr;}
''' + s[a:]
old='    std::string line;\n';assert s.count(old)==1
s=s.replace(old,'''    auto* channel=warlock_visual_channel_new();
    GObject* contexts[2]={G_OBJECT(g_object_new(G_TYPE_OBJECT,nullptr)),G_OBJECT(g_object_new(G_TYPE_OBJECT,nullptr))};
    bool outer[2]={true,true};
    for(int i=0;i<2;i++)g_object_weak_ref(contexts[i],finalized,&contexts[i]);
    std::string line;
''')
old='        if (op == "close") {';assert s.count(old)==1
s=s.replace(old,'''        if(op=="context-drop") {
            int index=json_object_get_int_member(object,"context");if(index<0 || index>1 || !outer[index])std::abort();
            outer[index]=false;g_object_unref(contexts[index]);ok=TRUE;
        } else if(op=="contexts") {
            auto* info=json_object_new();json_object_set_boolean_member(info,"firstAlive",contexts[0]!=nullptr);json_object_set_boolean_member(info,"secondAlive",contexts[1]!=nullptr);
            g_autoptr(JsonNode) node=json_node_new(JSON_NODE_OBJECT);json_node_take_object(node,info);output=json_to_string(node,FALSE);ok=TRUE;
        } else if(op=="channel" || op=="foreign-channel") {
            int index=json_object_get_int_member(object,"context");if(index<0 || index>1)std::abort();
            ChannelCall c{channel,policy,contexts[index],json_object_get_string_member(object,"action"),input};
            if(op=="foreign-channel") {auto* thread=g_thread_new("foreign-visual-channel",channel_call,&c);g_thread_join(thread);} else channel_call(&c);
            ok=c.ok;output=c.output;error=c.error;if(c.op=="close" && ok)channel=nullptr;
        } else if (op == "close") {''')
old='    return policy ? 5 : 0;';assert s.count(old)==1
s=s.replace(old,'''    for(int i=0;i<2;i++)if(outer[i])g_object_unref(contexts[i]);
    return policy || channel ? 5 : 0;''')
p=root/'native/visual-channel-fixture.cpp';assert not p.exists();p.write_text(s);print(p)
