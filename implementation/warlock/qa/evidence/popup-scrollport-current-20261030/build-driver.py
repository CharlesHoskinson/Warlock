import hashlib,importlib.util,json,os,pathlib,resource,subprocess,sys
R=pathlib.Path('/home/charles/Warlock')
B=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
sys.path.insert(0,str(R/'window-integration-qa'))
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
p=R/'implementation/warlock/adapter/current_build.py'
raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()=='d4e5af280a275f9a777322ee60f1f34bf21751b6726edcaa4e4105a02da4dbc7'
m=importlib.util.module_from_spec(importlib.util.spec_from_loader('current_build',loader=None));m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__)
node=pathlib.Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node');assert m.sha(node)=='caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943'
check=subprocess.run([str(node),'--check',str(R/'implementation/warlock/assets/popup-adapter.js')],capture_output=True,timeout=30)
(B/'pin-scrollport-node-check.stdout').write_bytes(check.stdout);(B/'pin-scrollport-node-check.stderr').write_bytes(check.stderr)
assert check.returncode==0
out=B/'pin-scrollport-build-root-v1'
report=m.build(B/'pin-scrollport-frontend-lock-root-v1.json','8f35f73022732f33f156f52488e327cf8cd5d6604be7d27cea0325ca2e054199',out)
assert report['passed']
receipt=out/'report.json';m.validate_report(receipt,m.sha(receipt))
print(json.dumps(dict(passed=True,nodeSyntaxExit=check.returncode,report=str(receipt),sha256=m.sha(receipt),nativeAcceptance=False,releaseAccepted=False)))
