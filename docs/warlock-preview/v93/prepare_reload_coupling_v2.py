"""Preserve schema check failure; compare binding with live original issued state."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent;old=docs/'couple_native184_known_reload.py'
receipt=docs/'reload-coupling-closed-command-schema-failure.json';assert not receipt.exists()
receipt.write_text(json.dumps({'scope':'af9a651cd7504b40ba4a169b3f9fe81f','script':str(old),'sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'exitCode':1,'failure':'TypeError before output creation: retired policy commands serialize as empty list, not live binding object.','correction':'Compare later binding with actual original native issued live state already retained by scenario; strict closed empty custody remains separately checked.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
s=old.read_text();needle="closed['privatePolicy']['commands']['binding']";assert s.count(needle)==1
s=s.replace(needle,"c['controlledOriginalNativeTicketsActuallyIssuedAndDelivered']['state']['privatePolicy']['commands']['binding']")
out=docs/'couple_native184_known_reload_v2.py';assert not out.exists();ast.parse(s);out.write_text(s);print(out)
