"""Add negative native channel API calls in a separate fixture derivative."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v119')
s=(root/'native/visual-channel-fixture.cpp').read_text();old='    else std::abort();';assert s.count(old)==1
s=s.replace(old,'''    else if(c.op=="attach-null-context")c.ok=warlock_visual_channel_attach(c.channel,c.policy,nullptr,&c.output,&c.error);
    else if(c.op=="attach-null-policy")c.ok=warlock_visual_channel_attach(c.channel,nullptr,c.context,&c.output,&c.error);
    else if(c.op=="attach-no-output")c.ok=warlock_visual_channel_attach(c.channel,c.policy,c.context,nullptr,&c.error);
    else if(c.op=="offer-no-output")c.ok=warlock_visual_channel_offer(c.channel,c.policy,c.context,nullptr,&c.error);
    else if(c.op=="retry-no-output")c.ok=warlock_visual_channel_retry(c.channel,c.policy,c.context,nullptr,&c.error);
    else if(c.op=="offer-null-context")c.ok=warlock_visual_channel_offer(c.channel,c.policy,nullptr,&c.output,&c.error);
    else if(c.op=="retry-null-context")c.ok=warlock_visual_channel_retry(c.channel,c.policy,nullptr,&c.output,&c.error);
    else if(c.op=="ack-no-input")c.ok=warlock_visual_channel_ack(c.channel,c.policy,c.context,nullptr,&c.error);
    else if(c.op=="current-null-policy")c.ok=warlock_visual_channel_current(c.channel,nullptr,c.context,&c.error);
    else std::abort();''')
p=root/'native/visual-channel-boundary-fixture.cpp';assert not p.exists();p.write_text(s);print(p)
