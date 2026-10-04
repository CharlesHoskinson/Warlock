import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
BASE=REPO/'implementation/elm-binding-registration-query-v579'
HELPER=REPO/'implementation/elm-native-grant-retirement-spike-v588'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=HELPER/'component-manifest.json'
assert sha(manifest)=='3e49a26733bb285f212b99b147e754293c425844677b52c777c34bb40ed774f0'
held=json.loads(manifest.read_text())
for rel,row in held['files'].items():
    assert sha(HELPER/rel)==row['sha256'] and (HELPER/rel).stat().st_size==row['size'],rel
for name in ['native','candidate']:shutil.copytree(BASE/name,ROOT/name)
shutil.copy2(BASE/'qa/build.py',ROOT/'qa/build.py')
shutil.copy2(HELPER/'native/grant-registry.hpp',ROOT/'native/grant-registry.hpp')
p=ROOT/'native/authority.cpp';s=p.read_text()
s=s.replace('#include "binding-registration.hpp"','#include "binding-registration.hpp"\n#include "grant-registry.hpp"\n#include <charconv>\n#include <memory>')
s=s.replace('std::map<pid_t, Session> sessions;','''std::map<pid_t, Session> sessions;
std::unique_ptr<Elm::GrantRetirement::Registry> grantRegistry;
uint64_t retirementSequence=0;
Elm::GrantRetirement::Peer verifiedPeer(pid_t pid,const std::string& start) {
    uint64_t ticks=0;
    const auto parsed=std::from_chars(start.data(),start.data()+start.size(),ticks);
    if(pid<=0 || parsed.ec!=std::errc{} || parsed.ptr!=start.data()+start.size() || ticks==0) throw std::runtime_error("unverified-peer");
    return {static_cast<uint64_t>(pid),ticks};
}''')
a=s.index('            std::erase_if(sessions,',s.index('operation == "hello"'))
b=s.index('session.geometryProtocol=0;',a)
s=s[:a]+'''            std::erase_if(sessions,[](const auto& entry) {
                if(startTime(entry.first)==entry.second.start) return false;
                grantRegistry->detach(verifiedPeer(entry.first,entry.second.start));return true;
            });
            const auto admitted=grantRegistry->hello(verifiedPeer(peer,start));
            if(admitted.status!=Elm::GrantRetirement::Status::Admitted) throw std::runtime_error("grant-bound-or-exhausted");
            if(!sessions.contains(peer)) sessions.emplace(peer,Session{start,admitted.binding.session,admitted.binding.frontend,0,0,"","",{}});
            auto& session=sessions.at(peer);
            session.id=admitted.binding.session;session.frontend=admitted.binding.frontend;
            '''+s[b:]
count=0
for before in ['*frontend!=found->second.frontend','*frontend != found->second.frontend']:
    count+=s.count(before)
    s=s.replace(before,before+' || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend})')
# Existing geometry, effect, registration, and snapshot/scene/trace groups.
assert count==4,count
needle='        } else if (operation=="binding-registration-request"'
branch='''        } else if ((operation=="binding-retire-request" || operation=="binding-retirement-state-request") && fields(object,{"protocolVersion","kind","binding","requestId","queriedBinding"})) {
            const auto bound=objectMember(object,"binding"),queried=objectMember(object,"queriedBinding");
            const auto requestId=counter(object,"requestId");
            if(!bound || !queried || !requestId || !fields(bound,{"lifetime","session","frontend"}) || !fields(queried,{"lifetime","session","frontend"})) throw std::runtime_error("retirement-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            const auto queriedNative=counter(queried,"lifetime"),queriedSession=counter(queried,"session"),queriedFrontend=counter(queried,"frontend");
            if(!native || !sessionId || !frontend || !queriedNative || !queriedSession || !queriedFrontend) throw std::runtime_error("retirement-schema");
            const auto found=sessions.find(peer);const auto caller=verifiedPeer(peer,start);
            const Elm::GrantRetirement::Binding callerBinding{*native,*sessionId,*frontend},targetBinding{*queriedNative,*queriedSession,*queriedFrontend};
            if(found==sessions.end() || found->second.start!=start || !grantRegistry->callerMatches(caller,callerBinding)) reply=error("binding-mismatch");
            else if(*queriedNative!=lifetime) reply=error("retirement-lifetime-mismatch");
            else if(retirementSequence==std::numeric_limits<uint64_t>::max()) reply=error("retirement-sequence-exhausted");
            else if(operation=="binding-retire-request" && callerBinding==targetBinding) reply=error("retirement-current-caller");
            else {
                using State=Elm::GrantRetirement::RetirementState;
                auto state=grantRegistry->retirementState(caller,callerBinding,targetBinding);
                if(state==State::Refused) reply=error("retirement-state-refused");
                else if(state==State::Future && operation=="binding-retire-request") reply=error("retirement-future-grant");
                else {
                    if(operation=="binding-retire-request" && state==State::Registered) {
                        if(grantRegistry->retire(caller,callerBinding,targetBinding)!=Elm::GrantRetirement::Status::Admitted) throw std::runtime_error("retirement-refused");
                        std::erase_if(sessions,[&](const auto& entry) { return entry.second.id==targetBinding.session && entry.second.frontend==targetBinding.frontend; });
                        state=grantRegistry->retirementState(caller,callerBinding,targetBinding);
                        if(state!=State::Retired) throw std::runtime_error("retirement-incomplete");
                    }
                    ++retirementSequence;
                    const auto queriedBinding="{\\"lifetime\\":"+quote(std::to_string(*queriedNative))+",\\"session\\":"+quote(std::to_string(*queriedSession))+",\\"frontend\\":"+quote(std::to_string(*queriedFrontend))+"}";
                    reply="{\\"protocolVersion\\":3,\\"kind\\":\\"binding-retirement\\",\\"retirementProtocol\\":1,\\"operation\\":"+quote(operation=="binding-retire-request"?"retire":"observe")+",\\"binding\\":"+binding(found->second)+",\\"requestId\\":"+quote(std::to_string(*requestId))+",\\"queriedBinding\\":"+queriedBinding+",\\"sequence\\":"+quote(std::to_string(retirementSequence))+",\\"grantState\\":"+quote(state==State::Retired?"Retired":state==State::Registered?"Registered":"Future")+"}";
                }
            }
'''+needle
assert s.count(needle)==1;s=s.replace(needle,branch)
s=s.replace('Elm::Registration::contains(sessions,*queriedSession,*queriedFrontend)','grantRegistry->registered({lifetime,*queriedSession,*queriedFrontend})')
s=s.replace('lifetime = randomIdentity();','lifetime = randomIdentity();\n    grantRegistry=std::make_unique<Elm::GrantRetirement::Registry>(lifetime);retirementSequence=0;',1)
s=s.replace('command.reset(); members.clear(); sessions.clear();','command.reset(); members.clear(); sessions.clear();grantRegistry.reset();')
p.write_text(s)
(ROOT/'SPEC.md').write_text('''# Native grant retirement authority

Parent579/owning205; frozen588 registry is owner-thread authoritative allocator and admission guard. Production starts lastIssued0 once per random native lifetime, never reseeds after detach/PID reuse. Server SO_PEERCRED PID and exact parsed nonzero kernel process-start ticks authenticate caller. All four existing binding branches additionally check registry callerMatches. Hello copies allocator fields into per-session geometry/effect metadata. Stale-peer removal detaches exact registry peer; explicit retirement erases exact registry and metadata grants. Retired IDs never return on reattach. Existing attached capabilities/payloads remain unchanged.

Exact-schema binding-retirement-state-request and binding-retire-request take current binding, requestId and queriedBinding. Reply binding-retirement/retirementProtocol1 echoes bindings/request, operation observe|retire, nonzero lifetime-scoped sequence and grantState Registered|Future|Retired. Allocated absent IDs/past frontends are Retired; future session IDs/frontends never certified. Self-query is Registered; explicit self/future/foreign grants refuse. Sequence exhaustion checked before mutation. Owner-thread reply is never an old effect settlement. Existing effects execute synchronous guarded callbacks.

No backend/C admission release, durable Unknown-history separation, current post-retirement observations, consumer proof validation or frontend retry is implemented. Actual native/coherent GUI qualification remains pending. Preserve failed590 verifier-shape and guard-count4-versus5 source preparation and no-source compile failures.594 correctly normalizes {sha256,size} inventories and targets the actual four inherited binding groups; producer588 is unchanged.
''')
u=json.loads((BASE/'upstream.json').read_text())
u['sourceFiles']={str(p.relative_to(ROOT)):sha(p) for folder in ['native','candidate'] for p in sorted((ROOT/folder).rglob('*')) if p.is_file()}
u['grantRegistryComponent']={'path':str(manifest),'sha256':sha(manifest)}
(ROOT/'upstream.json').write_text(json.dumps(u,indent=2)+'\n')
p=ROOT/'qa/build.py';p.write_text(p.read_text().replace('Read-only binding registration spike compiled against owning Core205; strong-symbol closure only, no loading or reconciliation acceptance','Monotonic grant retirement authority compiled against owning Core205; strong-symbol closure only, no loading or durable reconciliation acceptance'))
print(json.dumps({'producerFilesVerified':len(held['files']),'registryGuardedBindingGroups':count}))
