"""Retain exact build-local header directory aliases alongside regular file hashes."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).parent;p=root/'hold105-v3.py';assert not p.exists()
s=(root/'hold105-v2.py').read_text()
old='  assert not p.is_symlink(),p\n  if p.is_file():'
new='''  if p.is_symlink():
   assert base==plugin and p.name=='hyprland' and p.parent.name=='include' and p.parent.parent.name.startswith('build-'),p
   assert p.is_dir() and p.resolve()==(p.parent.parent/'owning-headers').resolve() and p.resolve().is_relative_to(base),p
   continue
  if p.is_file():'''
assert s.count(old)==1;s=s.replace(old,new)
old="'files':inventory(plugin)}";assert s.count(old)==1
new="'files':inventory(plugin),'directoryAliases':{str(p.relative_to(plugin)):str(p.resolve()) for p in plugin.rglob('*') if p.is_symlink()}}"
s=s.replace(old,new);p.write_text(s)
print('Fresh freezer validates only exact local owning-header directory aliases and inventories their targets')
