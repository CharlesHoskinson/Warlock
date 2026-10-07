"""Expose readonly original C recovery frontiers to coupled pressure traces."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v121')
s=(root/'native/policy-driver-output-gate-fixture.cpp').read_text();old='else if(op=="held-ticket")';assert s.count(old)==1
new='''else if(op=="output-state") {result=qa_withhold_original_output_capacity?"true":"false";ok=true;}
        else if(op=="recovery") {ok=warlock_imported_clients_control_recovery_begin(imported,popup,epoch,&text,&error);if(text){result=text;g_free(text);}}
        '''+old
s=s.replace(old,new);p=root/'native/policy-driver-output-model-fixture.cpp';assert not p.exists();p.write_text(s);print(p)
