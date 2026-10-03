"""Source reconstruction of exact inherited scopes; never runs native/UI input."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;QA=B.parent;P=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 checks={}
 checks['rootHelperExact']=sha(B/'root_pin_helper.py')==sha(P/'frontend/pin_helper.py')=='30cf295bbc3032b10996e9b6db7c602f6044d38cf73d4eb6ef917e72dd80f0f2'
 checks['nativeAuthorityExact']=sha(B/'native_authority.py')==sha(QA/'pin-native-qa-v1/case_authority.py')
 originals=('private_shell.py','helper_setup.py','helper_observer.py','service_observer.py','exec_gate.py','capture_evidence.py','verify_reversal.py','verify_c1.py','c1_pairing.py')
 checks['originalResponsiveC1ObserversExact']=all(sha(B/n)==sha(QA/'family-continuous-c1-v4'/n)for n in originals)
 old=QA/'toolkit-held-matrix-v14/frontend-candidate'
 checks['genuineFrontendProtocolAndTestsExact']=all(sha(B/'frontend-candidate'/n)==sha(old/n)for n in('native_frontend.py','test_frontend.py'))
 oldtext=(old/'prepare_config.py').read_text();newtext=(B/'frontend-candidate/prepare_config.py').read_text()
 checks['onlyResponsiveServicePairDelta']=newtext.replace('service-responsive-v13','service-review-v12')==oldtext
 original=(QA/'toolkit-held-matrix-v14/native-probe/probe.cpp').read_text();new=(B/'native-probe/probe.cpp').read_text()
 inverse=new.replace(' const auto keyboardSurface=g_pSeatManager->m_state.keyboardFocus.lock();\n const auto keyboardLayer=keyboardSurface?Desktop::viewState()->query().type(Desktop::View::VIEW_TYPE_LAYER_SURFACE).surface(keyboardSurface).runLayer():nullptr;\n std::string keyboardOwner="null";\n','',1).replace('if(layer==keyboardLayer)keyboardOwner=row;','',1).replace('+",\\\"keyboardSurfacePresent\\\":"+(keyboardSurface?"true":"false")+",\\\"keyboardLayerOwner\\\":"+keyboardOwner','',1)
 checks['inheritedReadonlyProbeExactOutsideAdditions']=inverse==original
 build=json.loads((B/'native-probe/build-report.json').read_text())
 checks['compiledReadonlyProbeExact']=build['exitCode']==0 and build['sourceUnchanged']is True and build['sourceSHA256']==sha(B/'native-probe/probe.cpp')and build['binarySHA256']==sha(B/'native-probe/libpin-frontend-probe.so')
 key=B/'keyboard';pkey=P/'keyboard-chords'
 text=(key/'physical_plan.c').read_text();oldtext=(pkey/'physical_plan.c').read_text()
 checks['onePhysicalSuperTBranch']=text.replace(' else if(!strcmp(argv[2],"super-t")){list[count++]=&META;list[count++]=&TKEY;}\n','',1)==oldtext
 # Retained source metadata gives the original exact frozen driver authority.
 known=json.loads((key/'inherited-keyboard-source.json').read_text())
 checks['physicalMapCanonicalBytesExact']=sha(key/'physical_keymap.inc')==sha(pkey/'physical_keymap.inc')
 for n in('physical_keyboard.c','physical_plan.h','physical_map_generator.c','physical_protocol_cpu.c','virtual-keyboard-client.h','virtual-keyboard-protocol.c','virtual-keyboard-unstable-v1.xml'):
  checks['unchangedPhysical_'+n]=sha(key/n)==sha(pkey/n)
 descriptor=json.loads((B/'payload-manifest.json').read_text())
 checks['allFrozenPayloadCopiesExact']=all(sha(row['source'])==row['sha256']==sha(B/'payload'/row['relative'])for row in descriptor['copies'])
 checks['allFrozenPayloadConfigExact']=all(sha(B/'payload'/name)==digest for name,digest in descriptor['generated'].items())
 checks['noWidgetSemanticsDelta']=all(sha(P/'frontend/widget_v66'/p.name)==sha(p)for p in (B/'payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v66').iterdir()if p.is_file())
 row=dict(result='pass'if all(checks.values())else'fail',checks=checks,nativeLaunch=False,projectedRuntimeTestsCounted=False)
 print(json.dumps(row,indent=2));return int(not all(checks.values()))
if __name__=='__main__':raise SystemExit(main())
