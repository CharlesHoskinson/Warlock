"""Extend the exact 110-command parent build with typed visual decoder controls."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v117');s=(root/'qa/build-native-policy.py').read_text()
old=" run('native-owned-policy-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/NativePreviewPolicy.elm','--optimize','--output=assets/native-preview-policy.js'])";assert s.count(old)==1
s=s.replace(old,old+"\n run('native-visual-decoder-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/NativePreviewVisualReplay.elm','--optimize','--output=assets/native-visual-decoder.js'])\n run('native-visual-decoder-boundaries',['node','qa/visual-codec-checks.js',str(OUT/'inputs/assets/native-visual-decoder.js')])")
ast.parse(s);p=root/'qa/build-visual-projection.py';assert not p.exists();p.write_text(s);print(p)
