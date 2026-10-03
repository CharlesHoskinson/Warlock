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
def verify_links(selected):
    for name,target in selected.items():
        path=Path(name)
        if not path.is_symlink()or os.readlink(path)!=target:raise ValueError('selected retained link changed: '+name)

def retained_file(name,digest,mode,expected_inputs,expected_modes,selected_links):
    path=Path(name);info=path.lstat();target=None;resolved=None
    if stat.S_ISLNK(info.st_mode):
        if name not in selected_links or os.readlink(path)!=selected_links[name]:raise ValueError('byte alias lacks exact selected target: '+name)
        target=selected_links[name];resolved=path.resolve(strict=True);backing=str(resolved)
        if backing not in expected_inputs or backing not in expected_modes or expected_inputs[backing]!=digest or expected_modes[backing]!=mode:raise ValueError('alias backing lacks exact captured bytes/mode: '+name)
        if not stat.S_ISREG(resolved.lstat().st_mode):raise ValueError('alias backing is not regular: '+name)
    elif not stat.S_ISREG(info.st_mode)or name in selected_links:raise ValueError('selected byte path kind conflicts: '+name)
    if sha(path)!=digest or stat.S_IMODE(path.stat().st_mode)!=mode:raise ValueError('selected retained bytes/mode changed: '+name)
    if target is not None and (not path.is_symlink()or os.readlink(path)!=target or path.resolve(strict=True)!=resolved):raise ValueError('selected alias changed during byte observation: '+name)

def retain(inputs,modes,links):
    def merge_file(name,digest,mode):
        if name in inputs and inputs[name]!=digest or name in modes and modes[name]!=mode:raise ValueError('selected closure file alias conflict: '+name)
        inputs[name]=digest;modes[name]=mode
    for path,expected,link_key in PACKETS:
        if path.is_symlink()or sha(path)!=expected:raise ValueError('selected closure packet changed: '+str(path))
        packet=json.loads(path.read_text())
        if set(packet['inputs'])!=set(packet['inputModes']):raise ValueError('complete selected input modes required')
        selected=dict(links)
        for name,target in packet[link_key].items():
            if name in selected and selected[name]!=target:raise ValueError('selected retained target conflict: '+name)
            selected[name]=target
        verify_links(selected)
        captured=dict(inputs);captured_modes=dict(modes)
        for name,digest in packet['inputs'].items():
            mode=packet['inputModes'][name]
            if name in captured and captured[name]!=digest or name in captured_modes and captured_modes[name]!=mode:raise ValueError('selected retained byte/mode conflict: '+name)
            captured[name]=digest;captured_modes[name]=mode
        for name,digest in packet['inputs'].items():retained_file(name,digest,packet['inputModes'][name],captured,captured_modes,selected)
        verify_links(selected)
        for name,digest in packet['inputs'].items():merge_file(name,digest,packet['inputModes'][name])
        links.update(selected)
        retained_file(str(path),expected,stat.S_IMODE(path.stat().st_mode),captured,captured_modes,selected)
        merge_file(str(path),expected,stat.S_IMODE(path.stat().st_mode))
