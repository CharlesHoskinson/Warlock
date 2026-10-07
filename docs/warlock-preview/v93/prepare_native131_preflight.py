"""Prepare coherent current native preflight without dropping historical source custody."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-client-provider-native-v131'
s=(root/'qa/prepare-current-provider-v3.py').read_text().replace('warlock-client-provider-native-v129','warlock-client-provider-native-v130').replace('warlock-preview-provider-v110','warlock-preview-provider-v119').replace('2517','2518').replace('Current held GUI110','Current held GUI119').replace('Original129/128/126','Original130/129/128/126').replace("pre['retainedNative129Report']","pre['retainedNative130Report']").replace('prepare-current-provider-v3-','prepare-current-provider-v4-')
a=s.index(" failed=root/'qa/prepare-current-provider-");b=s.index(' inputs[str(m)]',a);s=s[:a]+s[b:]
old="assert held['sourceHeld'] and held['passed'] and held['fullBuildCommands']==96 and held['originalBuildCommands']==95 and held['uriCChecks']==66 and held['uriStates']==320 and not held['webKitActivated'] and not held['nativeAcceptance']";assert s.count(old)==1
s=s.replace(old,"assert held['sourceHeld'] and held['passed'] and held['fullBuildCommands']==115 and held['originalBuildCommands']==112 and held['orderedVisualCustodyCPUQualified'] and not held['realHostPolicyActivated'] and not held['actualRendererProjectionActivated'] and not held['webKitActivated'] and not held['nativeAcceptance']")
s=s.replace("len(d['commands'])==96","len(d['commands'])==115")
s=s.replace('New URI router and controlled/scoped detachment protocol remain inactive.','New native persistent policy/visual channel/pure renderer and controlled/scoped detachment URI protocol remain inactive; this legacy campaign qualifies none of their new routes.')
ast.parse(s);p=root/'qa/prepare-current-provider-v4.py';assert not p.exists();p.write_text(s);print(p)
