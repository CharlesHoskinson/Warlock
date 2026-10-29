"""One reviewed recovery source delta over the unmodified current native verifier."""
import hashlib, importlib.util, json
from pathlib import Path
BASE=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
PRODUCT=Path('/home/charles/Warlock/implementation/warlock')
ORIGINAL=BASE/'context-keyup-qualified-terra-2-v1/fresh_candidate.py'
ORIGINAL_SHA='d1c69b53e0386ed2de96215294c3289d831c98ca12bfadff873c86ff5133ad9f'
REPORT=BASE/'context-keyup-qualified-terra-2-v1/native-new-instance-keyboard-1793299294154176471/report.json'
REPORT_SHA='69ab8850e0bf9f71cb90b6db76ded032fbc8ecc94b5eb3cc9a4a3fb1767cd48f'
NAME='adapter/recovery_profile.py'
OLD='651220f844591d5206b2f3f0f48fc2a652c7010d55cf796c1fda37cdc6adf6e8'
CURRENT='ace346503b5afd2c691748e7c2e1c25394fd81cc0a90be60525ff6cd85a78142'
def checked(path, expected):
    body=path.read_bytes()
    if hashlib.sha256(body).hexdigest()!=expected:raise RuntimeError('Qualified input changed: '+str(path))
    return body
def verify_sources():
    rows=json.loads(checked(REPORT,REPORT_SHA))['sourceInputs']
    if len(rows)!=367 or rows.get(NAME)!=OLD:raise RuntimeError('Historical source inventory mismatch')
    for name,expected in rows.items():
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:raise RuntimeError('Invalid source inventory path')
        checked(PRODUCT/relative,CURRENT if name==NAME else expected)
    return {'sourceInventoryReport':str(REPORT),'sourceInventoryReportSHA256':REPORT_SHA,'entries':len(rows),'onlyReviewedDelta':NAME,'historicalSHA256':OLD,'currentSHA256':CURRENT}
verify_sources()
checked(ORIGINAL,ORIGINAL_SHA)
spec=importlib.util.spec_from_file_location('current_context_qualified_candidate',ORIGINAL)
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
def verify_tuple():
    verify_sources()
    return original.verify_tuple()
class PrivateHyprSession(original.PrivateHyprSession):
    def __enter__(self):
        verify_sources()
        result=super().__enter__()
        try:
            verify_sources()
            return result
        except BaseException:
            self.host.close();raise
def __getattr__(name):return getattr(original,name)
