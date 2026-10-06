"""Add exact one-shot Elm readiness behind a real native receiver barrier."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v93'
target=root/'native/retirement-elm-channel-test-v4.cpp';assert not target.exists()
s=(root/'native/retirement-elm-channel-test-v3.cpp').read_text()
marker='    auto pending=[&] {';assert s.count(marker)==1
s=s.replace(marker,'    bool barrier=false;\n'+marker)
marker='                    }else if(kind=="retire-ready" || kind=="retire-delivery-ack") {';assert s.count(marker)==1
s=s.replace(marker,marker+'''\n                        if(kind=="retire-ready" && !barrier) {
                            check(endpoint.registerView(78,native.binding(),{1,2}),"Actual second native receiver blocks aggregate removal");barrier=true;
                        }
''')
marker='        }else if(op=="pending") {';assert s.count(marker)==1
s=s.replace(marker,'''        }else if(op=="blocked-poll") {
            const auto before=endpoint.native([](auto& broker){return broker.actorCount();});
            check(warlock_imported_clients_retirement_poll(owner,journal,popup,&events,&error) && events && !error && std::string_view(events)=="[]","Retained readiness cannot overrule existing receiver membership");
            check(endpoint.native([](auto& broker){return broker.actorCount();})==before,"Blocked polling cannot partially remove native maps");
            output("blocked",events);g_free(events);events=nullptr;
        }else if(op=="release-receiver") {
            require(barrier,"Actual receiver barrier installed");endpoint.unregisterView(78);
            check(warlock_imported_clients_retirement_poll(owner,journal,popup,&events,&error) && events && !error && std::string_view(events)!="[]","Original retained readiness completes after receiver clears without another Elm effect");
            output("controlled",events);g_free(events);events=nullptr;
'''+marker)
target.write_text(s)
target=root/'qa/retirement-native-elm-roundtrip-v3.js';assert not target.exists()
s=(root/'qa/retirement-native-elm-roundtrip-v2.js').read_text()
old=" const completed=await control({op:'controls',entries:result.commands});";assert s.count(old)==1
s=s.replace(old,""" const blocked=await control({op:'controls',entries:result.commands});assert.deepEqual(blocked.events,[]);checks++;
 const stillBlocked=await control({op:'blocked-poll'});assert.deepEqual(stillBlocked.events,[]);checks++;
 // Elm emitted its single readiness already. Only native receiver retirement
 // and revalidation of that retained input may unblock native completion.
 const completed=await control({op:'release-receiver'});""")
target.write_text(s)
target=root/'qa/retirement-native-elm-check-v4.py';assert not target.exists()
s=(root/'qa/retirement-native-elm-check-v3.py').read_text().replace('retirement-native-elm-check-v3','retirement-native-elm-check-v4').replace('native/retirement-elm-channel-test-v3.cpp','native/retirement-elm-channel-test-v4.cpp').replace('qa/retirement-native-elm-roundtrip-v2.js','qa/retirement-native-elm-roundtrip-v3.js')
ast.parse(s);target.write_text(s)
print(target)
