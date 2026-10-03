"""Pure unchanged QtV9 parent transport oracle; no runner imports/native actions."""
import ast,hashlib,re
from pathlib import Path
SOURCE=Path('/home/hoskinson/window-integration-qa/qt-modal-private-v9/run_native.py')

def transport_log_gate(logs):
 forbidden=r'\[libseat\]|DRM Backend failed|Starting the DRM backend|enabling fallbacks|error [0-9]+:|Broken pipe|parent transport failed|xdg_surface[^\n]*never[^\n]*configured'
 text='\n'.join(logs)
 return {'passed':'Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend' in text and bool(re.search(r'Output WAYLAND-1: configure surface with [0-9]+',text)) and not re.search(forbidden,text,re.I),'mandatoryMarker': 'Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend' in text,'configureHandlerObserved':bool(re.search(r'Output WAYLAND-1: configure surface with [0-9]+',text)),'forbiddenDiagnostics':re.findall(forbidden,text,re.I)}

def verify_authority(closure):
 if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=closure[str(SOURCE)]:raise RuntimeError('Exact primary transport source changed')
 original=next(n for n in ast.parse(SOURCE.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='transport_log_gate')
 own=next(n for n in ast.parse(Path(__file__).read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='transport_log_gate')
 if ast.dump(original,include_attributes=False)!=ast.dump(own,include_attributes=False):raise RuntimeError('Pure transport checker changed from primary source')
 return True
