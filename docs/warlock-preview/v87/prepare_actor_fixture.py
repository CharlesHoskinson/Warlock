"""Create synthetic peer-authenticated all-native transaction fixture."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v86')
text=(root/'native/retirement-observation-test.cpp').read_text()
text=text[:text.index('int main(int argc')]
text=text.replace('#include "preview_retirement.hpp"','#include "preview_retirement.hpp"\n#include "imported_clients.hpp"')
old='text=retirementReply(peer.pid,frontend,envelope.object(),mode);'
new='uint64_t retired=0;std::ifstream(root/"retired-through")>>retired;const auto subject=decimal(Json::text(envelope.object(),"subjectIncarnation"));text=retirementReply(peer.pid,frontend,envelope.object(),subject!=22 && subject<=retired?"retired":"valid");replace(text,"\\\"issuedThrough\\\":\\\"22\\\"","\\\"issuedThrough\\\":\\\"100000\\\"");'
assert old in text;text=text.replace(old,new)
old='text=scopeReply(peer.pid,frontend,envelope.object(),mode);'
new='uint64_t retired=0;std::ifstream(root/"retired-through")>>retired;const auto subject=decimal(Json::text(envelope.object(),"subjectIncarnation"));text=subject!=22 && subject<=retired?"{\\\"protocolVersion\\\":3,\\\"kind\\\":\\\"refused\\\",\\\"reason\\\":\\\"preview-client-scope-source-unavailable\\\"}":scopeReply(peer.pid,frontend,envelope.object(),mode);'
assert old in text;text=text.replace(old,new)
text+=(root/'qa/actor-retirement-main.cpp').read_text()
target=root/'native/actor-retirement-test.cpp';assert not target.exists();target.write_text(text)
print(target)
