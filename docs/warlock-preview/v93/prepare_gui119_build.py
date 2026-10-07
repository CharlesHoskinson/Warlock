"""Add pure renderer/channel compilation while retaining every original112 build command."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v119')
s=(root/'qa/build-visual-projection.py').read_text();old=" run('native-source-replay-build'";assert s.count(old)==1
insert=""" run('native-visual-receiver-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/NativePreviewReceiverReplay.elm','--optimize','--output=assets/native-visual-receiver.js'])
 run('native-visual-renderer-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/NativePreviewRenderer.elm','--optimize','--output=assets/native-visual-renderer.js'])
"""
s=s.replace(old,insert+old)
old="'elm-preview-policy.cpp']";assert s.count(old)==1;s=s.replace(old,"'elm-preview-policy.cpp','preview-visual-channel.cpp']")
old="str(OUT/'elm-preview-policy.cpp.o'),'-o'";assert s.count(old)==1;s=s.replace(old,"str(OUT/'elm-preview-policy.cpp.o'),str(OUT/'preview-visual-channel.cpp.o'),'-o'")
old="'elm-preview-policy.cpp.d']";assert s.count(old)==1;s=s.replace(old,"'elm-preview-policy.cpp.d','preview-visual-channel.cpp.d']")
ast.parse(s);p=root/'qa/build-visual-channel.py';assert not p.exists();p.write_text(s);print(p)
