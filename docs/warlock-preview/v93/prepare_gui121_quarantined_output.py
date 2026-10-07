"""Exercise already-returned native FD events after original urgent quarantine."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v121')
s=(root/'qa/policy-driver-positive-roundtrip.js').read_text()
old="const beforeOffer=await inspect();await one();const offered=await inspect();";assert s.count(old)==1
new="check((await call('quarantine',{epoch})).ok,'Original urgent quarantine conceals while offer/fence bytes remain retained');const beforeOffer=await inspect();check(!beforeOffer.privatePolicy.models[0].model.demand && beforeOffer.returnedEventBatches===1,'Quarantine retains original queued native output and known duty');await one();const offered=await inspect();";s=s.replace(old,new)
old="same(offered.privatePolicy.realm.ingress.pending,0,'Offer admission introduces no extra native acquisition');";assert s.count(old)==1
s=s.replace(old,"check(offered.privatePolicy.realm.ingress.pending>=beforeOffer.privatePolicy.realm.ingress.pending,'Original cleanup intents retained while admitted output takes priority');")
old="check(fenced.privatePolicy.models[0].model.image?.startsWith('elm-shell://preview/'),'Original offer/fence reaches the single policy drawable state');";assert s.count(old)==1
s=s.replace(old,"same(fenced.privatePolicy.models[0].model.image,null,'Late offer/fence cannot revive quarantined visuals');check(!fenced.privatePolicy.models[0].model.demand && fenced.privatePolicy.models[0].model.known.length===1,'Late output retains original known obligation without demand');")
p=root/'qa/policy-driver-quarantined-output-roundtrip.js';assert not p.exists();p.write_text(s)
s=(root/'qa/policy-driver-positive-check.py').read_text().replace('policy-driver-positive-check','policy-driver-quarantined-output-check').replace('policy-driver-positive-roundtrip.js','policy-driver-quarantined-output-roundtrip.js').replace('Actual original C capture via authenticated synthetic peer produces','Original urgent quarantine is processed after native data receipt/independent confirmation but before queued offer/fence admission. Late events must remain concealed and exact cleanup/scoped closure must still finish. Actual original C capture via authenticated synthetic peer produces')
ast.parse(s);p=root/'qa/policy-driver-quarantined-output-check.py';assert not p.exists();p.write_text(s);print(p)
