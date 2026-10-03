"""Reviewed private host V2 with a child-only Aquamarine negotiation repair."""
import hashlib
import importlib.util
import json
from pathlib import Path

STAGE=Path(__file__).resolve().parent
BASE=STAGE.parent/'private-weston-host-v2'
AQ=STAGE.parent/'aquamarine-version-guard-v1'
LIB=AQ/'prefix/lib/libaquamarine.so.0.15.0'
spec=importlib.util.spec_from_file_location('reviewed_original_weston_host_v2',BASE/'weston_host.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify_inputs():
    row=json.loads((STAGE/'frozen-inputs.json').read_text())
    for path,value in row['inputs'].items():
        if digest(path)!=value:raise RuntimeError('Host compatibility input changed: '+path)
    candidate=json.loads((AQ/'frozen-inputs.json').read_text())
    for path,value in candidate['inputs'].items():
        if digest(path)!=value:raise RuntimeError('Aquamarine compatibility input changed: '+path)
    for path,value in candidate['symlinks'].items():
        target=Path(path)
        if not target.is_symlink() or str(target.readlink())!=value:raise RuntimeError('Aquamarine loader symlink changed: '+path)

class ReviewedWestonHost(original.PrivateWestonHost):
    def __init__(self,output,main_env,width=1600,height=1000,dri_prime=None,mesa_vendor=False):
        private_parent=dict(main_env)
        private_parent['GSETTINGS_BACKEND']='memory'
        super().__init__(output,private_parent,width,height,dri_prime,mesa_vendor)
        self.evidence['privateSettingsBackend']='memory'

    def verify(self):
        super().verify();verify_inputs()
        self.evidence['privateAquamarine']={'path':str(LIB),'sha256':digest(LIB),'scope':'nested Hyprland child only; no installed replacement','contractManifestSHA256':digest(AQ/'frozen-inputs.json')}

    def launch(self,name,command,env=None):
        if name=='hyprland':
            verify_inputs()
            if not command or str(command[0])!='/usr/bin/Hyprland' or env is None:
                raise RuntimeError('Private library selection requires explicit reviewed child command/env')
            selected=dict(env)
            selected['LD_LIBRARY_PATH']=str(AQ/'prefix/lib')+':'+selected.get('LD_LIBRARY_PATH','')
            self.evidence['privateAquamarine']['childLibraryPath']=selected['LD_LIBRARY_PATH']
            return super().launch(name,command,selected)
        return super().launch(name,command,env)

class PrivateHyprSession(original.PrivateHyprSession):
    def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
        super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
        self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor)
        self.evidence=self.host.evidence
