from pathlib import Path
import sys,unittest
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();B=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v7');sys.path.insert(0,str(B))
import service_observer,module_binding
raw=module_binding._observe('independent-review-before-tests');assert not raw['errors']and len(raw['modules'])==19
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_actual_binding','test_batch_binding'])
result=unittest.TextTestRunner(verbosity=2).run(suite);raise SystemExit(not result.wasSuccessful()or bool(result.skipped))
