"""Exact inherited source/function conservation; no imports or runtime mutation."""
from pathlib import Path
import ast,copy,hashlib,json,stat,difflib
P=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-readonly-bounded-longevity-v22-runtime')
OLD=P.parent/'service-readonly-longevity-v21'
def sha(data):return hashlib.sha256(data).hexdigest()
def dump(node):return ast.dump(node,include_attributes=False)
def funcs(text):return {n.name:n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef)}
def source(text,node):return '\n'.join(text.splitlines()[node.lineno-1:node.end_lineno])
a=(OLD/'readonly_ipc.py').read_text();b=(P/'readonly_ipc.py').read_text();old=funcs(a);new=funcs(b)
checks=[];inverses={}
def check(label,ok):
 assert ok,label
 checks.append(label)
unchanged=set(old)-{'__init__','assert_closed','rotate_closed','query','_query','_validate_rows'}
for name in sorted(unchanged):check('exact inherited function '+name,source(a,old[name])==source(b,new[name]))
class AuthorityInverse(ast.NodeTransformer):
 def visit_Attribute(self,node):
  self.generic_visit(node)
  if (node.attr=='issuerSHA256' and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='_current_authority'):
   call=node.value
   check('typed authority substitution has no positional arguments',not call.args)
   check('typed authority substitution has only initial borrow=True or no keywords',not call.keywords or len(call.keywords)==1 and call.keywords[0].arg=='borrow' and isinstance(call.keywords[0].value,ast.Constant) and call.keywords[0].value.value is True)
   return ast.Call(func=ast.Attribute(value=ast.Name(id='self',ctx=ast.Load()),attr='authority',ctx=ast.Load()),args=[],keywords=[])
  return node
node=AuthorityInverse().visit(copy.deepcopy(new['_query']));check('entire original _query inverse AST exact',dump(node)==dump(old['_query']));inverses['_query']=ast.unparse(node)
def inverse_text(name,changes):
 text=source(b,new[name])
 for before,after in changes:
  check(name+' inverse exact fragment '+before.strip().splitlines()[0],before in text)
  text=text.replace(before,after)
 parsed=ast.parse(__import__('textwrap').dedent(text)).body[0]
 check('entire '+name+' inverse AST exact',dump(parsed)==dump(old[name]));inverses[name]=text
inverse_text('__init__',[
 ('        self.current_source = material_path(readonly_current.__file__)\n',''),
 ("'archiveSource': self.archive_source, 'currentSource': self.current_source,","'archiveSource': self.archive_source,"),
 ('        self.current = None\n',''),
 ('        self.authority()  # Full history before constructing any current-only proof.','        self.authority()'),
 ('        self.current = CurrentReads(self.archive, self.lease, self.issuer, self.predecessor)\n','')])
inverse_text('query',[
 ("        borrowed = getattr(self.local,'borrowed',None)\n        if borrowed is None:self.local.borrowed = borrowed = []\n        borrowed.append(None)\n",''),
 ('            tip = borrowed.pop()\n            if tip is not None:self.current.release(tip,borrow=True)\n','')])
inverse_text('_validate_rows',[("    current_source = original_issuer.pop('currentSource', None)\n    if current_source != material_path(Path(__file__).with_name('readonly_current.py')):\n        raise ValueError('retained current-read source replaced')\n",'')])
inverse_text('rotate_closed',[
 ('        prepared = None\n        adopted = False\n',''),
 ('self._current_authority().issuerSHA256','self.authority()'),
 ("            old_token = self.current.latest.token.verify()\n            prepared = self.current.prepare(pointer,old_tip,old_epoch+1,old_token['archivedCount']+len(candidates),self.issuer)\n",''),
 ('                self.current.adopt(prepared,old_tip)\n                adopted = True\n',''),
 ('            if prepared is not None and not adopted: prepared.close()\n','')])
# The inherited closure predicate/assertion is exact, surrounded by proven append/full-audit/FD retirement guards.
body=new['assert_closed'].body
inner=body[1].body[0]
check('original assert_closed reservation/row guard AST exact',dump(inner)==dump(old['assert_closed'].body[0]))
check('normal-close rotation try/finally structure',isinstance(body[1],ast.Try) and len(body[1].body)==3 and len(body[1].finalbody)==1)
check('normal-close full audit precedes current FD retirement',ast.unparse(body[1].body[1])=='self.audit_history()' and ast.unparse(body[1].body[2])=='self.current.close()')
check('normal-close finally releases rotation',ast.unparse(body[1].finalbody[0])=='self.rotation.release()')
check('new methods are exactly reviewed owner/current/audit additions',set(new)-set(old)=={'_read_owner','_current_authority','audit_history'})
# Sole inherited fixture hook: same function after precisely reversing instrumentation targets/keyword forwarding.
x=(OLD/'test_readonly_longevity.py').read_text();y=(P/'test_readonly_longevity.py').read_text()
reverse=y.replace('original=self.reader._current_authority','original=self.reader.authority').replace('def blocked(*,borrow=False):','def blocked():').replace('return original(borrow=borrow)','return original()').replace('self.reader._current_authority=blocked','self.reader.authority=blocked')
check('whole inherited test file inverse byte exact',reverse==x)
xf,yf=funcs(x),funcs(y)
changed=[n for n in xf if source(x,xf[n])!=source(y,yf[n])]
check('sole fixture function changed',changed==['test_live_postdisk_confirmation_reference_cannot_be_reclaimed'])
for name in xf:
 if name in changed:
  xa=[dump(n) for n in ast.walk(xf[name]) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr.startswith('assert')]
  ya=[dump(n) for n in ast.walk(yf[name]) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr.startswith('assert')]
  check('all sole-fixture assertions AST exact',xa==ya)
original=json.loads((P/'runtime-authorized-provenance.json').read_text())['inheritedTopSources'];delta=[]
for n,item in original.items():
 check('original mode '+n,stat.S_IMODE((P/n).stat().st_mode)==item['mode'])
 check('ancestor bytes '+n,sha((OLD/n).read_bytes())==item['sha256'])
 if sha((P/n).read_bytes())!=item['sha256']:delta.append(n)
check('only two inherited files differ',set(delta)=={'readonly_ipc.py','test_readonly_longevity.py'})
report={'version':1,'checks':checks,'passed':True,'existingChangedFiles':delta,'inheritedTopSourceCount':len(original),'unchangedFunctions':sorted(unchanged),'newFunctions':sorted(set(new)-set(old)),'wholeFunctionInverses':inverses,'fixtureInverseByteExact':True,'allOriginalAssertionsAndDeadlinesUnchanged':True,'nativeEffectRecoveryFilesExact':True,'nativeLaunch':False,'sources':{str(P/n):sha((P/n).read_bytes()) for n in ('readonly_ipc.py','readonly_current.py','test_readonly_longevity.py','test_readonly_current.py')}}
Path('/tmp/v22_source_inverse_result.json').write_text(json.dumps(report,indent=2)+'\n')
for n in delta:Path('/tmp/v22-'+n+'.diff').write_text(''.join(difflib.unified_diff((OLD/n).read_text().splitlines(True),(P/n).read_text().splitlines(True),fromfile=str(OLD/n),tofile=str(P/n))))
print(json.dumps({'passed':True,'checks':len(checks),'inherited':len(original),'delta':delta}))
