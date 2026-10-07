"""Extend actual held 108-command build, preserving failed older entry evidence."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v116'
source=(root/'qa/build-retained-ingress-v2.py').read_text()
old=" run('popup-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Popup.elm','--optimize','--output=assets/popup.js'])"
assert source.count(old)==1
source=source.replace(old,old+"\n run('native-owned-policy-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/NativePreviewPolicy.elm','--optimize','--output=assets/native-preview-policy.js'])")
old=" for name in ['preview_uri.cpp','preview-uri-router.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp']:"
assert source.count(old)==1;source=source.replace(old,old.replace("'imported-clients.cpp']","'imported-clients.cpp','elm-preview-policy.cpp']"))
old="str(OUT/'imported-clients.cpp.o'),'-o',str(OUT/'elm-host')";assert source.count(old)==1;source=source.replace(old,"str(OUT/'imported-clients.cpp.o'),str(OUT/'elm-preview-policy.cpp.o'),'-o',str(OUT/'elm-host')")
old=" for dependency_file in ['host.d','preview_uri.cpp.d','preview_icons.cpp.d','preview-uri-webkit.cpp.d','preview-provider-bootstrap.cpp.d','client-producer.cpp.d','imported-clients.cpp.d']:"
assert source.count(old)==1;source=source.replace(old,old.replace("'imported-clients.cpp.d']","'imported-clients.cpp.d','preview-uri-router.cpp.d','elm-preview-policy.cpp.d']"))
ast.parse(source);target=root/'qa/build-native-policy.py';assert not target.exists();target.write_text(source)
# The failed report retains the exact modified older build.py in its own inputs.
# Restore this historical entry from its held parent, without touching that proof.
(root/'qa/build.py').write_bytes((repo/'implementation/warlock-preview-provider-v115/qa/build.py').read_bytes())
print(target)
