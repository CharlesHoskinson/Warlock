"""Create reviewable code from complete exact host methods; never launch/import it."""
import ast,difflib,json,hashlib,textwrap
from pathlib import Path
B=Path(__file__).resolve().parent
O=B/'proposed';O.mkdir(exist_ok=True)
def method(text,cls,name):
 tree=ast.parse(text);c=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
 node=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name==name)
 return ''.join(text.splitlines(True)[node.lineno-1:node.end_lineno])
boot=(B/'inverses/bootstrap-host.py').read_text();old=(B/'inverses/original-host.py').read_text()
launch=method(boot,'ReviewedWestonHost','launch').replace("str(command[0])!='/usr/bin/Hyprland'","str(command[0])!=str(CORE)").replace("return super().launch(name,command,selected)","return original.PrivateWestonHost.launch(self,name,command,selected)").replace("            verify_inputs()\n","            verify_inputs(); verify_pair()\n")
wait=method(boot,'ReviewedWestonHost','wait_socket').replace("row.get('command',[None])[0]=='/usr/bin/Hyprland'","row.get('command',[None])[0]==str(CORE)")
entry=textwrap.indent(textwrap.dedent(method(old,'PrivateHyprSession','__enter__')),'    ').replace("['/usr/bin/Hyprland','--config',str(config)]","[str(CORE),'--config',str(config)]")
header='''"""Proposed exact candidate child selectors. No side effects before context entry."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,socket,struct,subprocess,time
QA=Path('/home/hoskinson/window-integration-qa')
CANDIDATE=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
CORE=CANDIDATE/'build-core-make/Hyprland'
B=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('_pin_v3_exact_bootstrap_host',QA/'private-weston-aq-bootstrap-host-v5/weston_host.py')
accepted=importlib.util.module_from_spec(spec);spec.loader.exec_module(accepted)
original=accepted.original;AQ=accepted.AQ
from host_observation import ObservedShutdownMixin
verify_inputs=accepted.verify_inputs
effective_lua=original.effective_lua;nested_base=original.nested_base
socket_identity=original.socket_identity;process=original.process;mapped_files=original.mapped_files
digest=original.digest

def verify_pair():
    import pair_binding
    return pair_binding.read_pair(B/'PAIR_READY.json')

class ReviewedWestonHost(ObservedShutdownMixin,accepted.ReviewedWestonHost):
    _original_module=original
'''
text=header+launch+'\n'+wait+'''
class PrivateHyprSession(accepted.PrivateHyprSession):
    def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
        super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
        self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor)
        self.evidence=self.host.evidence
'''+entry+'\n'
ast.parse(text);(O/'candidate_host.py').write_text(text)
rows=[]
for cls,name,original,changed in [('ReviewedWestonHost','launch',method(boot,'ReviewedWestonHost','launch'),launch),('ReviewedWestonHost','wait_socket',method(boot,'ReviewedWestonHost','wait_socket'),wait),('PrivateHyprSession','__enter__',method(old,'PrivateHyprSession','__enter__'),entry)]:
 rows.append(dict(className=cls,method=name,originalSHA256=hashlib.sha256(original.encode()).hexdigest(),proposedSHA256=hashlib.sha256(changed.encode()).hexdigest()))
(B/'host-whole-methods.diff').write_text(''.join(difflib.unified_diff((method(boot,'ReviewedWestonHost','launch')+'\n'+method(boot,'ReviewedWestonHost','wait_socket')+'\n'+textwrap.indent(textwrap.dedent(method(old,'PrivateHyprSession','__enter__')),'    ')).splitlines(True),(launch+'\n'+wait+'\n'+entry).splitlines(True),fromfile='exact-host-methods-before',tofile='exact-candidate-host-methods-proposed')))
(B/'host-method-inverses.json').write_text(json.dumps(dict(nativeExecuted=False,methods=rows),indent=2)+'\n')
print('proposed host parsed; three complete owning methods bound')
