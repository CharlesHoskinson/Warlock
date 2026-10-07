"""Retain the freezer schema failure and prepare exact-schema validation."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
d=pathlib.Path(__file__).parent;p=d/'hold_combined_restart_204_207.py';out=d/'hold_combined_restart_204_207_v2.py';assert not out.exists()
assert not (d/'component-report-combined-restart-204-207.json').exists()
failure={'passed':False,'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'error':"AttributeError: 'list' object has no attribute 'values'",'componentManifestsWritten':False,'scope':'Packaging-only freezer schema failure. Native reports unchanged; no native acceptance downgrade or claim.'}
(d/'combined-freezer-schema-failure.json').write_text(json.dumps(failure,indent=2)+'\n')
s=p.read_text().replace("d['previewFixtureCleanupExits'].values()","d['previewFixtureCleanupExits']").replace("'controlled-native-readers-revoked:',","'controlled-native-reader-held:','controlled-native-reader-probed:',")
assert s!=p.read_text();ast.parse(s);out.write_text(s);print(out)
