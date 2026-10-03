"""Actual imported source/location preflight; no host enter or native launch."""
from pathlib import Path
import sys,ast,copy,importlib.util,json,argparse
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
P=Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-controller-v1-proposal')
V2=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v2')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def verify(manifest):
 runner=load('_promoted_b_actual_runner',B/'run_native.py');packet=runner.verify(manifest)
 host=runner.original.module('_promoted_b_actual_host_preflight',B/'host/candidate_host.py')
 lua=(V2.parent/'browser-files-flow-v20/nested-qt.lua').read_bytes()+(V2/'private-controls.lua').read_bytes()
 session=host.PrivateHyprSession(B/'attempt-999/host',{},1600,1000,lua)
 expected=B/'attempt-999/host'
 assert runner.B==B and host.B==B and session.host.output==expected and session.host.runtime is None and session.host.processes==[]
 source=Path('/home/hoskinson/window-integration-qa/private-weston-host-v2/weston_host.py')
 tree=ast.parse(source.read_bytes());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=='PrivateWestonHost');method=next(x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name=='__enter__');guard=next(x for x in method.body if isinstance(x,ast.Assert)and 'startswith'in ast.unparse(x.test));code=compile(ast.Expression(copy.deepcopy(guard.test)),str(source),'eval')
 assert eval(code,{'str':str,'Path':Path,'self':session.host})is True
 old=host.PrivateHyprSession(P/'attempt-999/host',{},1600,1000,lua)
 assert eval(code,{'str':str,'Path':Path,'self':old.host})is False
 return dict(result='pass',inputs=len(packet['inputs']),links=len(packet['symlinks']),directories=len(packet['directoryModes']),actualRunnerB=str(runner.B),actualHostOutput=str(session.host.output),originalGuardQA=True,originalGuardSPEC=False,hostEntered=False,nativeLaunched=False)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,default=B/'SOURCE_INPUTS-v2.json');a=ap.parse_args();print(json.dumps(verify(a.inputs)))
