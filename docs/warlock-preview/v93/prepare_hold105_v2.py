"""Fresh freezer accepts absolute report paths as well as Path objects."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).parent;p=root/'hold105-v2.py';assert not p.exists()
s=(root/'hold105.py').read_text();old='sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()';assert s.count(old)==1
p.write_text(s.replace(old,'sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()'))
print('Fresh freezer path conversion fixed; original failed freezer unchanged')
