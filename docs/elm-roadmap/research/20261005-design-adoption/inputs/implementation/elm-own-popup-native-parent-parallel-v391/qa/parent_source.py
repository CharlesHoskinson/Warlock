"""Exact declared caller delta, not permission to remove arbitrary wrappers."""
import ast,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
PARENT_MAP='''def parent_map():
 try:return timing.call('privateParentMap',boot,lambda:parent_collect(parent_collector,guard,pid=parent['pid'],start=int(parent['start']),pgid=int(parent['pgid']),deadline=boot))
 except BaseException as failure:
  r['parentMapGuardRefusal']=repr(failure)
  try:r['sameReadParentMapFailure']=map_failure.archive(failure,out/'parent-map-failure',pid=parent['pid'],start=parent['start'])
  except BaseException as archive_error:r['parentMapFailureArchiveError']=repr(archive_error)
  raise
'''
WRAPPER_LOADER="def checked_parent(guard, guard_files):\n    import hashlib, importlib.util, stdlib_origin\n    path = ROOT / 'qa/parent_loader.py'\n    raw = stdlib_origin.read(path)\n    if hashlib.sha256(raw).hexdigest() != '54e0d908ad067f0ae8eaef334e798c17df89f18875439ac7a0187d982feb0a9e':\n        raise ValueError('parent wrapper source changed')\n    expected = compile(raw, str(path), 'exec', dont_inherit=True, optimize=sys.flags.optimize)\n    cache = pathlib.Path(importlib.util.cache_from_source(str(path)))\n    files = {str(path): '54e0d908ad067f0ae8eaef334e798c17df89f18875439ac7a0187d982feb0a9e'}\n    if cache.exists() or cache.is_symlink():\n        cached = stdlib_origin.read(cache)\n        stdlib_origin.cache_code(cached, expected)\n        files[str(cache)] = hashlib.sha256(cached).hexdigest()\n    spec = importlib.util.spec_from_file_location('verified_parent_wrapper391', path)\n    module = importlib.util.module_from_spec(spec)\n    sys.modules[spec.name] = module\n    exec(expected, module.__dict__)\n    previous = stdlib_origin.CRITICAL\n    stdlib_origin.CRITICAL = {**previous, module.__name__: ('checked_parent', 'QualifiedParent', 'qualify_module', 'verified')}\n    try:\n        stdlib_origin.loaded_code(module, expected, path, cache, raw)\n    finally:\n        stdlib_origin.CRITICAL = previous\n    qualified, dependencies = module.checked_parent(guard, guard_files, wrapper=(module, raw, path))\n    files.update(dependencies)\n    return (qualified, files)\n"
EXTERNAL_VALIDATOR="def parent_collect(qualified,guard,*,pid,start,pgid,deadline):\n # Validate from the source-executed entry before any wrapper-owned method.\n import hashlib,importlib.util,stdlib_origin\n remaining(deadline)\n wrapper,wrapper_raw,wrapper_path=qualified.wrapper\n if wrapper_path!=ROOT/'qa/parent_loader.py' or type(wrapper_raw) is not bytes or hashlib.sha256(wrapper_raw).hexdigest()!='54e0d908ad067f0ae8eaef334e798c17df89f18875439ac7a0187d982feb0a9e':raise ValueError('external parent wrapper origin')\n def validate(module,raw,path,digest,critical):\n  if type(raw) is not bytes or hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('external parent code buffer')\n  expected=compile(raw,str(path),'exec',dont_inherit=True,optimize=sys.flags.optimize)\n  previous=stdlib_origin.CRITICAL;stdlib_origin.CRITICAL={**previous,module.__name__:critical}\n  try:stdlib_origin.loaded_code(module,expected,path,pathlib.Path(importlib.util.cache_from_source(str(path))),raw)\n  finally:stdlib_origin.CRITICAL=previous\n validate(wrapper,wrapper_raw,wrapper_path,'54e0d908ad067f0ae8eaef334e798c17df89f18875439ac7a0187d982feb0a9e',('checked_parent','QualifiedParent','qualify_module','verified'))\n if type(qualified) is not wrapper.QualifiedParent or qualified.guard is not guard or 'collect' in qualified.__dict__ or 'qualify' in qualified.__dict__:raise ValueError('external parent instance binding')\n if qualified.path!=ROOT.parent/'elm-own-popup-parent-map-parallel-v382/parent_maps.py' or qualified.guard_path!=ROOT.parent/'elm-own-popup-runtime-index-guard-v364/guard.py':raise ValueError('external parent dependency path')\n validate(qualified.module,qualified.raw,qualified.path,'ae370586e5957100e13d1b940f8bc59c8f52fc6864b8721b833429719572f6e9',('collect','_parallel_rows','Refused'))\n validate(guard,qualified.guard_raw,qualified.guard_path,'785a2c3b1717e949ed5628eb7048479c6c8897560be55b50117f098625bb71a9',('fingerprint','process_identity','parse_maps','map_identity','read_text_bounded','remaining','_MountInfo','Refused','UncertainWorkers'))\n remaining(deadline)\n return wrapper.QualifiedParent.collect(qualified,pid=pid,start=start,pgid=pgid,deadline=deadline)\n"
QUALIFICATION="parent_collector,parent_files=timing.call('parentCollectorQualification',None,lambda:checked_parent(guard,guard_files))"
def original(source):
 tree=ast.parse(source);counts={'loader':0,'external':0,'qualification':0,'inputs':0,'wrapper':0,'callback':0,'fallback':0}
 class Normalize(ast.NodeTransformer):
  def visit_FunctionDef(self,n):
   if n.name=='parent_collect':assert ast.dump(n)==ast.dump(ast.parse(EXTERNAL_VALIDATOR).body[0]);counts['external']+=1;return None
   if n.name=='checked_parent':assert ast.dump(n)==ast.dump(ast.parse(WRAPPER_LOADER).body[0]);counts['loader']+=1;return None
   if n.name=='parent_map':assert ast.dump(n)==ast.dump(ast.parse(PARENT_MAP).body[0]);counts['wrapper']+=1;return None
   return self.generic_visit(n)
  def visit_Assign(self,n):
   if ast.dump(n)==ast.dump(ast.parse(QUALIFICATION).body[0]):counts['qualification']+=1;return None
   if ast.dump(n)==ast.dump(ast.parse('pm=parent_map()').body[0]):counts['callback']+=1;return ast.parse("pm=timing.call('privateParentMap',boot,lambda:host.original.mapped_files(parent['pid']))").body[0]
   return self.generic_visit(n)
  def visit_Expr(self,n):
   if ast.dump(n)==ast.dump(ast.parse("r['inputs'].update(parent_files)").body[0]):counts['inputs']+=1;return None
   return self.generic_visit(n)
  def visit_If(self,n):
   self.generic_visit(n)
   if isinstance(n.test,ast.BoolOp) and ast.dump(n.test.values[-1])==ast.dump(ast.parse("'parentMapGuardRefusal' not in r",mode='eval').body):counts['fallback']+=1;n.test.values.pop()
   return n
 normalized=Normalize().visit(tree);assert all(v==1 for v in counts.values()),counts
 baseline=ast.parse((ROOT.parent/'elm-own-popup-native-budget-timing-v373/qa/native.py').read_bytes());assert ast.dump(normalized,include_attributes=False)==ast.dump(baseline,include_attributes=False);return normalized
