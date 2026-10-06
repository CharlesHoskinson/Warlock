"""Correct request-counter audit: Native.next issues, rather than peeks."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v86')
old=r/'native/actor-retirement-test-v2.cpp';target=r/'native/actor-retirement-test-v3.cpp';assert not target.exists()
text=old.read_text()
for name in ['nextBeforeForeign','afterRetirement']:
 a='native.next()=='+name;b='native.next()=='+name+'+1';assert text.count(a)==1;text=text.replace(a,b)
target.write_text(text)
text=(r/'qa/actor-retirement-check-v2.py').read_text().replace('actor-retirement-check-v2-','actor-retirement-check-v3-').replace('native/actor-retirement-test-v2.cpp','native/actor-retirement-test-v3.cpp')
# Full diagnostics remain in artifact logs; bounded console reports.
text=text.replace("'error':report.get('error')","'error':str(report.get('error',''))[:600]")
(r/'qa/actor-retirement-check-v3.py').write_text(text)
print(target)
