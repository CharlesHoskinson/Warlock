"""Exercise actual C/native journal route with original aggregate obligations."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v90')
p=r/'native/actor-retirement-channel-test-v1.cpp';assert not p.exists()
s=(r/'native/actor-retirement-test-v3.cpp').read_text()
start=s.index(' auto retire=[&]');end=s.index(' auto terminal=[&]',start)
s=s[:start]+r'''
 std::string deferredAck;const uint64_t lastSubject=mode=="turnover"?300:23;
 auto retirementPending=[&] {
  char* text=nullptr;check(warlock_imported_clients_retirement_pending(owner,journal,popup,&text,&error) && text && !error,"Original native completion journal read");
  std::string result=text;g_free(text);return result;
 };
 auto retire=[&](uint64_t subject,bool expected) {
  const auto identity="family:"+std::to_string(subject);char* json=nullptr;
  check(warlock_imported_clients_retirement_observe(owner,popup,identity.c_str(),&json,&error) && json && !error,"Actual original-receiver retirement observation");
  const std::string encoded=json;g_free(json);json=nullptr;Json observed("{\"rows\":"+encoded+"}");
  auto rows=json_object_get_array_member(observed.object(),"rows");require(rows,"Observation array");
  if(json_array_get_length(rows)==0){check(!expected,"Active source yields no retirement readiness grant");return;}
  check(json_array_get_length(rows)==1,"One retained exact native observation");
  auto original=json_node_get_object(json_array_get_element(rows,0));
  const auto ready=Wire().text("kind","retire-ready").begin("binding").binding(native.binding()).end().counter("subject",subject)
   .text("observationRequest",Json::text(original,"request")).text("observationSequence",Json::text(original,"sequence")).finish();
  const auto before=native.next();auto bad=ready;replace(bad,"\"subject\":\""+std::to_string(subject)+"\"","\"subject\":\"999999\"");
  check(!warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),bad.c_str(),&json,&error) && !json && error,"Mismatched readiness refused before native query");g_clear_error(&error);
  check(native.next()==before+1,"Mismatched readiness consumes no native query");
  check(warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),ready.c_str(),&json,&error) && json && !error,"Actual readiness validates native aggregate transaction");
  std::string result=json;g_free(json);json=nullptr;Json completed("{\"rows\":"+result+"}");
  auto deliveries=json_object_get_array_member(completed.object(),"rows");require(deliveries,"Completion array");
  check((json_array_get_length(deliveries)==1)==expected,"Actual physical/journal/receiver guards determine completion");
  if(!expected)return;
  auto delivery=json_node_get_object(json_array_get_element(deliveries,0));
  check(std::string_view(Json::text(delivery,"kind"))=="native-actor-retirement-delivery","Completion has independent typed delivery identity");
  auto final=Json::child(delivery,"fact");
  check(std::string_view(Json::text(final,"kind"))=="native-actor-retired" && decimal(Json::text(final,"subject"))==subject &&
    decodeBinding(Json::child(final,"binding"))==native.binding(),"Exact retained native aggregate fact");
  const auto ordinal=decimal(Json::text(delivery,"deliveryOrdinal"));
  check(retirementPending()==result && retirementPending()==result,"Lost completion remains byte-identical after native actor erasure");
  const auto acknowledged=Wire().text("kind","retire-delivery-ack").begin("binding").binding(native.binding()).end().counter("deliveryOrdinal",ordinal).finish();
  const auto gap=Wire().text("kind","retire-delivery-ack").begin("binding").binding(native.binding()).end().counter("deliveryOrdinal",ordinal+1).finish();
  check(!warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),gap.c_str(),&json,&error) && !json && error,"Future delivery ACK cannot skip retained completion");g_clear_error(&error);
  check(retirementPending()==result,"Gap ACK retains original final fact");
  auto foreignPopup=reinterpret_cast<gpointer>(uintptr_t(78));
  check(!warlock_imported_clients_retirement_pending(owner,journal,foreignPopup,&json,&error) && !json && error,"Foreign popup cannot read completion journal");g_clear_error(&error);
  if(subject==lastSubject){deferredAck=acknowledged;return;}
  check(warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),acknowledged.c_str(),&json,&error) && json && !error,"Original processing acknowledgment confirms final delivery");g_free(json);json=nullptr;
  check(retirementPending()=="[]","Confirmed completion alone removed from transport journal");
  check(warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),acknowledged.c_str(),&json,&error) && json && !error,"Lost ACK replay confirms without actor lookup or recreation");g_free(json);
 };
''' +s[end:]
old=' check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Actual original C drain and close");warlock_preview_bootstrap_free(bootstrap);server.finish();'
assert s.count(old)==1
s=s.replace(old,r'''
 check(!deferredAck.empty() && retirementPending()!="[]","Final unacknowledged completion remains after all physical jobs drain");
 const bool emptyBeforeConfirmation=warlock_imported_clients_empty(owner);
 const bool closeRefused=!warlock_imported_clients_close(owner,&error);
 if(!closeRefused) {
  owner=nullptr;g_clear_error(&error);warlock_preview_bootstrap_free(bootstrap);server.finish();
  check(false,"UnconfirmedRetirementCompletionMustPreventNativeOwnerClose");
 }
 check(error && !emptyBeforeConfirmation,"Empty predicate includes retained retirement delivery");g_clear_error(&error);
 char* confirmation=nullptr;const auto lastIdentity="family:"+std::to_string(lastSubject);
 check(warlock_imported_clients_retirement_control(owner,journal,popup,lastIdentity.c_str(),deferredAck.c_str(),&confirmation,&error) && confirmation && !error,"Original final acknowledgment completes retained close barrier");g_free(confirmation);
 check(warlock_imported_clients_empty(owner) && retirementPending()=="[]" && warlock_imported_clients_close(owner,&error) && !error,"Actual original C drain and confirmed delivery close");warlock_preview_bootstrap_free(bootstrap);server.finish();
''')
p.write_text(s)
p=r/'qa/actor-retirement-channel-check-v1.py';assert not p.exists()
s=(r/'qa/actor-retirement-check-v3.py').read_text().replace('actor-retirement-check-v3-','actor-retirement-channel-check-v1-').replace('native/actor-retirement-test-v3.cpp','native/actor-retirement-channel-test-v1.cpp')
s=s.replace('Sequential synthetic subjects greater than256 and retained live neighbor are CPU qualification','Retained exact observations, typed readiness, independent completion ordinals, loss/retry/gap/epoch barriers and shutdown confirmation are additional C/native gates. Synthetic readiness is not compiled Elm settlement. Sequential synthetic subjects greater than256 and retained live neighbor are CPU qualification')
ast.parse(s);p.write_text(s)
