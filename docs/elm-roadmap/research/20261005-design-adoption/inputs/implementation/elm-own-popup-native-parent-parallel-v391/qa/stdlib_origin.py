"""Substantive source/cache/loaded-code qualification before guard import."""
import ast,hashlib,importlib,importlib.util,io,json,marshal,os,pathlib,stat,struct,sys,types
class Refused(ValueError):pass
LIMIT=32*1024*1024
MODULES={'threading':'threading.py','concurrent.futures.thread':'concurrent/futures/thread.py','concurrent.futures._base':'concurrent/futures/_base.py'}
CRITICAL={'threading':('Thread','Condition','current_thread'),'concurrent.futures.thread':('ThreadPoolExecutor','_WorkItem','_python_exit'),'concurrent.futures._base':('Future','Executor','wait')}
def require(ok,message):
 if not ok:raise Refused(message)
def read(path):
 path=pathlib.Path(path)
 try:fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NONBLOCK|os.O_NOFOLLOW)
 except OSError as e:raise Refused('stdlib file open') from e
 try:
  first=os.fstat(fd);require(stat.S_ISREG(first.st_mode) and first.st_size<=LIMIT,'stdlib file bound/type');f=os.fdopen(fd,'rb')
 except BaseException:os.close(fd);raise
 with f:
  raw=f.read(LIMIT+1);last=os.fstat(f.fileno());require(len(raw)<=LIMIT,'stdlib byte bound')
  linked=path.stat(follow_symlinks=False)
  def identity(s):return s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns
  require(identity(first)==identity(last)==identity(linked),'stdlib file changed')
 return raw

def codes(code):
 found={}
 def collect(c):
  found.setdefault(c.co_qualname,[]).append(c)
  for value in c.co_consts:
   if type(value) is types.CodeType:collect(value)
 collect(code);return found

def same_constant(actual,expected):
    if type(actual) is not type(expected):return False
    if type(actual) is types.CodeType:return same_code(actual,expected)
    if type(actual) is tuple:return len(actual)==len(expected) and all(same_constant(a,e) for a,e in zip(actual,expected))
    if type(actual) is float:return struct.pack('!d',actual)==struct.pack('!d',expected)
    if type(actual) is complex:return same_constant(actual.real,expected.real) and same_constant(actual.imag,expected.imag)
    if type(actual) is frozenset:return {(type(v),repr(v)) for v in actual}=={(type(v),repr(v)) for v in expected}
    return actual==expected

def same_code(actual,expected):
    if type(actual) is not types.CodeType or type(expected) is not types.CodeType:return False
    fields=('co_argcount','co_posonlyargcount','co_kwonlyargcount','co_nlocals','co_stacksize','co_flags','co_code','co_names','co_varnames','co_filename','co_name','co_qualname','co_firstlineno','co_linetable','co_exceptiontable','co_freevars','co_cellvars')
    return all(getattr(actual,k)==getattr(expected,k) for k in fields) and same_constant(actual.co_consts,expected.co_consts)

def cache_code(raw,expected):
 require(type(raw) is bytes and len(raw)<=LIMIT and len(raw)>=16,'stdlib cache bound')
 require(raw[:4]==importlib.util.MAGIC_NUMBER and int.from_bytes(raw[4:8],'little') in (0,1,3),'stdlib cache header')
 stream=io.BytesIO(raw[16:])
 try:code=marshal.load(stream)
 except (ValueError,EOFError,TypeError) as e:raise Refused('stdlib cache decode') from e
 require(same_code(code,expected),'stdlib cached code differs from pinned source')
 # Reject trailing marshal records as well as malformed module types.
 require(stream.tell()==len(raw)-16,'stdlib cache trailing bytes')
 return code

def bindings(source):
    functions={};classes={};imports={}
    def walk(body,scope,target):
        for node in body:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                kind='function';accessor=None
                for d in node.decorator_list:
                    if isinstance(d,ast.Name) and d.id in ('staticmethod','classmethod','property'):
                        kind=d.id
                        if kind=='property':accessor='fget'
                    elif isinstance(d,ast.Attribute) and d.attr in ('setter','getter','deleter'):
                        kind='property';accessor={'setter':'fset','getter':'fget','deleter':'fdel'}[d.attr]
                line=min([node.lineno]+[d.lineno for d in node.decorator_list]);definition=(scope+node.name,line)
                if kind=='property':
                    row=target.setdefault(node.name,{'kind':kind,'accessors':{}});row['accessors'][accessor]=[definition]
                else:target[node.name]={'kind':kind,'definitions':[definition]}
            elif isinstance(node,ast.ClassDef):
                members={};walk(node.body,scope+node.name+'.',members);classes[node.name]=members
            elif isinstance(node,ast.ImportFrom) and not scope:
                for alias in node.names:imports[alias.asname or alias.name]=(node.module,alias.name)
            elif isinstance(node,(ast.Assign,ast.AnnAssign)):
                targets=node.targets if isinstance(node,ast.Assign) else [node.target]
                if isinstance(node.value,ast.Name):
                    for key in targets:
                        if isinstance(key,ast.Name) and node.value.id in target:target[key.id]=dict(target[node.value.id])
                        if not scope and isinstance(key,ast.Name) and node.value.id in imports:imports[key.id]=imports[node.value.id]
                elif isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='classmethod' and len(node.value.args)==1 and ast.dump(node.value.args[0])==ast.dump(ast.parse('types.GenericAlias',mode='eval').body):
                    for key in targets:
                        if isinstance(key,ast.Name):target[key.id]={'kind':'generic-alias'}
            else:
                for attr in ('body','orelse','finalbody'):
                    value=getattr(node,attr,None)
                    if isinstance(value,list):walk(value,scope,target)
                for handler in getattr(node,'handlers',[]):walk(handler.body,scope,target)
    walk(ast.parse(source).body,'',functions);return functions,classes,imports

def loaded_code(module,expected,path,cache,source):
    require(type(module) is types.ModuleType and module.__file__==str(path),'stdlib loaded file origin')
    require(module.__spec__ is not None and module.__spec__.origin==str(path),'stdlib loaded spec origin')
    require(module.__cached__==str(cache),'stdlib loaded cache origin')
    expected_codes=codes(expected);functions,classes,imports=bindings(source);seen=[]
    def check(fn,definitions):
        require(type(fn) is types.FunctionType and fn.__module__==module.__name__ and fn.__globals__ is module.__dict__,f'stdlib callable module/globals owner: {getattr(fn, "__qualname__", repr(fn))} module={getattr(fn, "__module__", None)} globals={getattr(fn, "__globals__", {}).get("__name__")}')
        code=fn.__code__;require((code.co_qualname,code.co_firstlineno) in definitions,'stdlib callable assigned to wrong slot')
        require(any(same_code(code,e) for e in expected_codes.get(code.co_qualname,[])),'stdlib loaded code differs from pinned source');seen.append(code.co_qualname)
    for name in CRITICAL[module.__name__]:require(name in module.__dict__,'stdlib required binding missing')
    for name,value in module.__dict__.items():
        if name in functions:
            # Pinned threading source explicitly has a Python fallback for
            # these two native _thread bindings; qualify the active C identity.
            if name in imports and imports[name][0]=='_thread' and type(value) in (types.BuiltinFunctionType,type):
                native=importlib.import_module('_thread');require(value is getattr(native,imports[name][1]) and value.__module__=='_thread' and value.__name__==imports[name][1] and value.__qualname__==imports[name][1],'stdlib native fallback binding differs')
            else:check(value,functions[name]['definitions'])
        elif name in classes:
            require(isinstance(value,type) and value.__module__==module.__name__ and value.__qualname__==name,'stdlib class binding owner');members=classes[name]
            for member_name,row in members.items():
                slot=('_'+name.lstrip('_')+member_name) if member_name.startswith('__') and not member_name.endswith('__') else member_name
                require(slot in value.__dict__,f'stdlib declared member missing: {module.__name__}.{name}.{slot}');member=value.__dict__[slot];kind=row['kind']
                if kind=='function':check(member,row['definitions'])
                elif kind in ('staticmethod','classmethod'):
                    require(type(member) is {'staticmethod':staticmethod,'classmethod':classmethod}[kind],'stdlib declared descriptor kind');check(member.__func__,row['definitions'])
                elif kind=='property':
                    require(type(member) is property,'stdlib declared property kind')
                    for accessor in ('fget','fset','fdel'):
                        fn=getattr(member,accessor)
                        if accessor in row['accessors']:check(fn,row['accessors'][accessor])
                        else:require(fn is None,'stdlib undeclared property accessor')
                else:require(kind=='generic-alias' and type(member) is classmethod and member.__func__ is types.GenericAlias,'stdlib foreign factory differs')
            for member_name,member in value.__dict__.items():
                if type(member) in (types.FunctionType,staticmethod,classmethod,property):require(member_name in members or any(member_name=='_'+name.lstrip('_')+key for key in members if key.startswith('__') and not key.endswith('__')),'stdlib undeclared member')
        elif type(value) is types.FunctionType and value.__module__==module.__name__:raise Refused('stdlib undeclared module callable')
    require(bool(seen),'stdlib loaded code coverage empty');return sorted(set(seen))

def qualify(pin_raw,pin_path,verified_files,supplement_raw,supplement_path):
 require(type(pin_raw) is bytes,'stdlib pin bytes');pin=json.loads(pin_raw);require(set(pin)=={'pythonVersion','files','scope'} and type(pin['files']) is dict,'stdlib pin shape')
 require(pin['pythonVersion']==sys.version,'stdlib interpreter version');require(type(verified_files) is dict and str(pin_path) in verified_files and hashlib.sha256(pin_raw).hexdigest()==verified_files[str(pin_path)],'stdlib pin not validated')
 supplement=json.loads(supplement_raw);require(type(supplement_raw) is bytes and set(supplement)=={'files','scope'} and str(supplement_path) in verified_files and hashlib.sha256(supplement_raw).hexdigest()==verified_files[str(supplement_path)],'stdlib supplement not validated')
 rows={**pin['files'],**supplement['files']};require(len(rows)==len(pin['files'])+len(supplement['files']),'stdlib supplement overlaps');executable=pathlib.Path(sys.executable).resolve();require(str(executable) in rows,'stdlib executable unpinned');files={};buffers={}
 for p,w in rows.items():
  require(type(p) is str and pathlib.Path(p).is_absolute() and type(w) is str and len(w)==64,'stdlib pin row');raw=read(p);require(hashlib.sha256(raw).hexdigest()==w,'stdlib source/executable changed');files[p]=w;buffers[p]=raw
 require(len(rows)==4,'stdlib pinned module inventory')
 actual=pathlib.Path('/proc/self/exe').stat();disk=executable.stat();require((actual.st_dev,actual.st_ino)==(disk.st_dev,disk.st_ino) and pathlib.Path('/proc/self/exe').resolve()==executable,'stdlib executing interpreter differs');modules={}
 # Compile verified buffer only. Never execute an expected stdlib copy: doing
 # so would mutate threading main-thread/atexit state.
 for name,suffix in MODULES.items():
  paths=[pathlib.Path(p) for p in rows if p.endswith('/'+suffix)];require(len(paths)==1,'stdlib source inventory');p=paths[0]
  try:expected=compile(buffers[str(p)],str(p),'exec',dont_inherit=True,optimize=sys.flags.optimize)
  except (SyntaxError,ValueError) as e:raise Refused('stdlib pinned source compile') from e
  cache=pathlib.Path(importlib.util.cache_from_source(str(p)))
  if cache.exists() or cache.is_symlink():
   raw=read(cache);cache_code(raw,expected);files[str(cache)]=hashlib.sha256(raw).hexdigest()
  module=importlib.import_module(name);covered=loaded_code(module,expected,p,cache,buffers[str(p)]);modules[name]={'source':str(p),'cache':str(cache),'cachePresent':str(cache) in files,'verifiedCodeQualnames':covered}
 require(sys.modules['concurrent.futures.thread']._base is sys.modules['concurrent.futures._base'],'stdlib Future module linkage differs')
 require(sys.modules['concurrent.futures.thread'].threading is sys.modules['threading'],'stdlib threading module linkage differs')
 aggregator=importlib.import_module('concurrent.futures');require(aggregator.ThreadPoolExecutor is sys.modules['concurrent.futures.thread'].ThreadPoolExecutor,'stdlib executor aggregator binding differs')
 return {'files':files,'modules':modules,'guardNotImportedYet':True,'nativeAcceptance':False,'scope':'Verified compiled source and current cache/loaded Python code; mutable module data is not a native authority proof'}
