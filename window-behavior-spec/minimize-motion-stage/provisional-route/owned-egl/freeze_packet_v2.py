#!/usr/bin/env python3
"""Offline packet builder. Does not open a Wayland/EGL connection."""
import hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ATLAS=HERE.parent.parent/'cross-output-design'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(name,args,expected=None):
 result=subprocess.run(args,cwd=HERE,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 path=HERE/(name+'.v2.log');path.write_text(result.stdout)
 assert result.returncode==0,(args,result.stdout[-2000:])
 if expected:assert expected in result.stdout,(args,'unexpected count')
 return {'command':args,'exit':result.returncode,'log':str(path),'sha256':sha(path)}
checks=[run('ledger',['./test-commit-ledger'],'80 owned EGL commit ledger checks PASS'),run('commands',['./test-renderer-commands'],'20 actual owned-renderer pending-command checks PASS'),run('backend',['./test-backend-policy'],'15 reviewed GPU backend policy checks PASS'),run('observer',['python3','-m','unittest','-v','test_native_observer.py'],'Ran 5 tests'),run('typecheck',['quint','typecheck','owned_commit_test.qnt']),run('scenarios',['quint','test','owned_commit_test.qnt'],'13 passing'),run('samples',['quint','run','owned_commit.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--verbosity=1'],'No violation found')]
files=[HERE/f for f in ('Renderer.cpp','CommitLedger.hpp','BackendPolicy.hpp','test_commit_ledger.cpp','test_renderer_commands.cpp','test_backend_policy.cpp','owned_commit.qnt','owned_commit_test.qnt','CONTRACT.md','Makefile','README.md','hypr-motion-renderer-staged','test-commit-ledger','test-renderer-commands','test-backend-policy','native_observer.py','test_native_observer.py','nested_owned_egl_smoke.py','freeze_packet_v2.py')]
files+=list(HERE.glob('*-client.h'))+list(HERE.glob('*-protocol.c'))+list((HERE/'primary-source').glob('*'))
files+=[ATLAS/f for f in ('nested-stable.lua','nested_preservation.py','snapshot_fixture.py','native-atlas-v18/hyprbars-v18-atlas-candidate.so','native-atlas-v18/main.cpp')]
files+=[Path('/usr/share/wayland-protocols')/f for f in ('stable/presentation-time/presentation-time.xml','stable/viewporter/viewporter.xml','unstable/xdg-output/xdg-output-unstable-v1.xml','staging/fractional-scale/fractional-scale-v1.xml','stable/xdg-shell/xdg-shell.xml')]
files+=[Path('/home/hoskinson/src/quickshell-accessibility/src/wayland/wlr_layershell/wlr-layer-shell-unstable-v1.xml')]
linked=subprocess.check_output(['ldd',str(HERE/'hypr-motion-renderer-staged')],text=True)
files+=[Path(p) for p in re.findall(r'(?:=> )?(/[^\s]+)',linked)]
inputs={str(p.resolve()):sha(p.resolve()) for p in files}
manifest={'scope':'Offline-owned EGL v2; native command not run','inputs':inputs}
path=HERE/'native-manifest-v2.json';path.write_text(json.dumps(manifest,indent=2)+'\n')
packet={'nativeTested':False,'installed':False,'serviceIntegrated':False,'scope':'one-window producer only; synthetic private icon; production controller unchanged','counts':{'ledger':80,'actualCommandConsumer':20,'backend':15,'observer':5,'formalNamed':13,'formalSamples':2000,'formalMaxSteps':100},'checks':checks,'nativeManifest':{'path':str(path),'sha256':sha(path)},'rendererSHA256':sha(HERE/'hypr-motion-renderer-staged'),'sourceInputs':inputs,'primarySources':{'mesa':'https://archive.mesa3d.org/mesa-26.2.2.tar.xz','refreshCounter':'https://registry.khronos.org/OpenGL/extensions/OML/GLX_OML_sync_control.txt'},'mesaArchiveSHA256':sha(Path('/tmp/owned-egl-mesa-source.tar.xz')),'backendPolicy':'Exact Mesa26.2.2 token; software/swrast/llvmpipe/softpipe/SWR/Zink excluded before source upload/readiness','presentationCounterPolicy':'Zero valid; equal MSC permitted with newer local sequence/time; backward non-wrap rejected; uint64 natural wrap allowed','reviewRepairs':['shared batch progress','early feedback accepted only on own successful swap, original scene telemetry','output removal defers destruction during swap','latest pending token owns cancel','exact release token boundary'],'nativeCommand':['python3',str(HERE/'nested_owned_egl_smoke.py'),'--output','/home/hoskinson/.cache/window-owned-egl-private-v2']}
(HERE/'checkpoint-v2.json').write_text(json.dumps(packet,indent=2)+'\n')
print(json.dumps({'renderer':packet['rendererSHA256'],'manifest':sha(path),'packet':sha(HERE/'checkpoint-v2.json'),'inputs':len(inputs),'counts':packet['counts']}))
