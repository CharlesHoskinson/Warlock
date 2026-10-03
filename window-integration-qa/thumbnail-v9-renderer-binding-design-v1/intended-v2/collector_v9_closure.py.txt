"""Exact selected closure union. Import starts no resources."""
import hashlib,json,os,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
DESIGN=QA/'thumbnail-v9-renderer-binding-design-v1'
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
PACKETS=((SERVICE/'manifest-family-preparation-v24.json','b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c','links'),
 (QA/'family-preparation-thumbnail-v7/frozen-inputs.json','d066ecf9b9ec94f0fe096d117464ba0f611f5b4d655792c0f1f8c6c339cd90eb','symlinks'),
 (QA/'thumbnail-v8-terminal-source-handoff-v1.json','4a9bb60a64b884cbe87a747446757336e646600a588a7d06e16e1f8511aac5aa','symlinks'),
 (DESIGN/'retained-components-v2.json','38733576f1da4e40596f261730c931ddf72cf2c27075c476664516298340a43c','symlinks'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def retain(inputs,modes,links):
    def add_file(name,digest,mode):
        path=Path(name);info=path.lstat()
        if not stat.S_ISREG(info.st_mode)or path.is_symlink()or sha(path)!=digest or stat.S_IMODE(info.st_mode)!=mode:raise ValueError('selected retained file changed: '+name)
        if name in links or name in inputs and inputs[name]!=digest or name in modes and modes[name]!=mode:raise ValueError('selected closure file alias conflict: '+name)
        inputs[name]=digest;modes[name]=mode
    for path,expected,link_key in PACKETS:
        if path.is_symlink()or sha(path)!=expected:raise ValueError('selected closure packet changed: '+str(path))
        packet=json.loads(path.read_text())
        if set(packet['inputs'])!=set(packet['inputModes']):raise ValueError('complete selected input modes required')
        for name,digest in packet['inputs'].items():add_file(name,digest,packet['inputModes'][name])
        for name,target in packet[link_key].items():
            if not Path(name).is_symlink()or os.readlink(name)!=target or name in inputs or name in modes or name in links and links[name]!=target:raise ValueError('selected retained link changed/conflicts: '+name)
            links[name]=target
        add_file(str(path),expected,stat.S_IMODE(path.stat().st_mode))
