"""Produce bounded instrumentation derivatives; retain exact upstream imports."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-hidden-capture-fusion-v29'
class Instrument(ast.NodeTransformer):
 def visit_FunctionDef(self,node):
  self.generic_visit(node)
  phase={'capture_source':'capture_source','_capture_source_impl':'capture_source_impl','_capture_hidden_fused':'hidden_capture','finish_capture_previews':'preview_finish'}.get(node.name)
  if phase:node.body=[ast.With(items=[ast.withitem(ast.Call(ast.Name('span',ast.Load()),[ast.Constant(phase)],[]))],body=node.body)]
  if node.name=='send':node.body.insert(0,ast.Expr(ast.Call(ast.Name('observed_command',ast.Load()),[ast.Name('message',ast.Load())],[])))
  return node
 def visit_With(self,node):
  self.generic_visit(node)
  for item in node.items:
   value=item.context_expr
   if isinstance(value,ast.Attribute) and value.attr in ('capture_lock','snapshot_lock'):
    item.context_expr=ast.Call(ast.Name('measured_lock',ast.Load()),[value,ast.Constant(value.attr)],[])
  return node
 def visit_Call(self,node):
  self.generic_visit(node)
  if isinstance(node.func,ast.Attribute):
   phase={'run':'helper','check_output':'query','clients':'query','check_current':'identity_check'}.get(node.func.attr)
   if phase and ast.unparse(node.func.value) in ('self.commands','self.base','self'):
    return ast.Call(ast.Name('measured_call',ast.Load()),[ast.Constant(phase),node.func,*node.args],node.keywords)
  return node
 def visit_Assign(self,node):
  self.generic_visit(node)
  if any(isinstance(t,ast.Name) and t.id=='event' for t in node.targets) and ast.unparse(node.value)=='json.loads(line)':
   return [node,ast.Expr(ast.Call(ast.Name('observed_event',ast.Load()),[ast.Name('event',ast.Load())],[]))]
  return node
manifest={'original_root':str(SOURCE),'files':[]}
for name in ('native_desktop.py','pipe_transport.py'):
 original=(SOURCE/name).read_bytes();tree=ast.parse(original);tree=Instrument().visit(tree);ast.fix_missing_locations(tree)
 content='from phase_trace import span, measured_lock, measured_call, observed_event, observed_command\n'+ast.unparse(tree)+'\n'
 if name=='native_desktop.py':content=content.replace("Path(__file__).with_name('production_motion_6d9.py')",repr(str(SOURCE/'production_motion_6d9.py'))).replace("source = "+repr(str(SOURCE/'production_motion_6d9.py')),"source = Path("+repr(str(SOURCE/'production_motion_6d9.py'))+")")
 (ROOT/name).write_text(content)
 manifest['files'].append({'name':name,'original_sha256':hashlib.sha256(original).hexdigest(),'derivative_sha256':hashlib.sha256(content.encode()).hexdigest()})
(ROOT/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
