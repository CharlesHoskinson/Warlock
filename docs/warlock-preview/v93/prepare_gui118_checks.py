"""Extend original C/JSC/visual proofs with readonly creator-owned custody."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v118')
s=(root/'native/persistent-policy-native-fixture-v3.cpp').read_text();old='  else if(op=="policy-close-probe")';assert s.count(old)==1
s=s.replace(old,'  else if(op=="policy-visuals") {ok=warlock_preview_policy_visual_projection(policy,&text,&error);if(text)result=take(text);}\n'+old);p=root/'native/persistent-policy-native-fixture-v4.cpp';assert not p.exists();p.write_text(s)
s=(root/'qa/persistent-policy-visual-roundtrip.js').read_text();s=s.replace('let visualChecks=0;','let visualChecks=0;let readonlyChecks=0;')
old=' if(result.visuals!==null){';assert s.count(old)==1
s=s.replace(old," const current=await call('policy-visuals');if(result.realm.closed || !result.realm.controlled){assert(!current.ok && current.refused && current.result===null,'Absent/closed native authority refuses current projection');readonlyChecks++;}else{assert(current.ok && !current.refused,'Creator-owned readonly visual copy');assert.deepEqual(current.result,result.visuals,'Readonly query returns only latest exact successful visual data');readonlyChecks+=2;}\n"+old)
old=' let setup=await next(),epoch=setup.epoch;';assert s.count(old)==1;s=s.replace(old,old+"const beforeGrant=await call('policy-visuals');assert(!beforeGrant.ok && beforeGrant.refused && beforeGrant.result===null,'No automatic authority from native factory creation');readonlyChecks++;")
s=s.replace('visualProjectionChecks:visualChecks,','readonlyProjectionChecks:readonlyChecks,visualProjectionChecks:visualChecks,');p=root/'qa/readonly-visual-native-roundtrip.js';assert not p.exists();p.write_text(s)
s=(root/'qa/persistent-policy-visual-native-check.py').read_text().replace('persistent-policy-visual-native-check-','readonly-visual-native-check-').replace('qa/persistent-policy-visual-native-check.py','qa/readonly-visual-native-check.py').replace('qa/persistent-policy-visual-roundtrip.js','qa/readonly-visual-native-roundtrip.js').replace('native/persistent-policy-native-fixture-v3.cpp','native/persistent-policy-native-fixture-v4.cpp')
s=s.replace("e['visualProjectionChecks']>0", "e['visualProjectionChecks']==90 and e['readonlyProjectionChecks']>0")
s=s.replace("'scope':'Original207 controls", "'scope':'Readonly native projection getter invokes no Elm, emits no commands/diagnostic model and allocates no native ordinal. Original207 controls")
ast.parse(s);p=root/'qa/readonly-visual-native-check.py';assert not p.exists();p.write_text(s);print(p)
