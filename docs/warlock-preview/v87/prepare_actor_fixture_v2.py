"""Fresh corrected fixture; retain original compile failure and inputs."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v86')
old=r/'native/actor-retirement-test.cpp';target=r/'native/actor-retirement-test-v2.cpp';assert not target.exists()
text=old.read_text();a='preview::uri::Endpoint foreign({256,8,2,4096},4,2);';b='preview::uri::Endpoint foreign({256,8,2,4096},4,2,[](uint64_t)->std::optional<preview::uri::NativeTime>{return {};});'
assert a in text;target.write_text(text.replace(a,b))
text=(r/'qa/actor-retirement-check.py').read_text().replace('actor-retirement-check-','actor-retirement-check-v2-').replace('native/actor-retirement-test.cpp','native/actor-retirement-test-v2.cpp')
(r/'qa/actor-retirement-check-v2.py').write_text(text)
print(target)
