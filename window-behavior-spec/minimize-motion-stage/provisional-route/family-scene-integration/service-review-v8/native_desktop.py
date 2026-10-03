"""Native adapter candidate. Instantiate only under a coordinated GUI grant.

Uses the exact frozen production planner/core semantics. V18 canonical atlas
capture adds whole-window cross-output coordinates without geometry writes.
Translucent client backdrop equivalence remains outside the capture guarantee.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import importlib.util
import uuid
import production_motion_6d9 as production
from scene_controller import key, rectangle
from snapshot_cache import SnapshotCache

class NativeDesktop:
    def __init__(self, root, *, core, target=None, cache_root=None):
        self.root=Path(root)
        expected=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-window-motion'
        if not self.root.resolve().is_relative_to(expected.resolve()) or self.root.resolve()==expected.resolve():
            raise ValueError('actor snapshot root must be under private motion runtime')
        self.root.mkdir(parents=True,mode=0o700,exist_ok=False)
        self.root.chmod(0o700)
        # Each actor receives an independent exact production module. ROOT and
        # CORE in frozen methods cannot be overwritten by another family actor.
        source=Path(__file__).with_name('production_motion_6d9.py')
        if hashlib.sha256(source.read_bytes()).hexdigest()!='6d9a21114cfc9d8ed4a4669bb4c1a585375abd56bf27de2783e203926dcecbaa':
            raise ValueError('frozen native planner source changed')
        spec=importlib.util.spec_from_file_location('motion_native_'+uuid.uuid4().hex,source)
        self.production=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.production)
        self.production.ROOT=self.root
        self.production.CORE=Path(core)
        self.base=self.production.Desktop()
        self.target_override=target
        self.capture_serial=0
        self.capture_session=os.urandom(6).hex()
        self.capture_lock=threading.RLock()
        self.shared_cache=SnapshotCache(cache_root,self.base.validate_snapshot,session=os.environ['HYPRLAND_INSTANCE_SIGNATURE']) if cache_root else None
        self.current_capture_epoch=None
    def __getattr__(self,name):return getattr(self.base,name)
    def target(self,window):
        return self.target_override(window) if self.target_override else self.base.target(window)
    def capture_source(self,window,scene_token,index):
        with self.capture_lock:
            self.current_capture_epoch=None
            try:
                if self.shared_cache and window.get('workspace',{}).get('name')=='special:win-minimized':
                    metadata,pixels=self.shared_cache.restore(window)
                    self.check_current(window)
                    stem=self.shared_cache.stem(window)
                    for extension,data in (('.png',pixels),('.json',json.dumps(metadata).encode())):
                        path=self.root/(stem+extension)
                        staging=self.root/(stem+'-'+uuid.uuid4().hex+extension+'.tmp')
                        try:
                            with os.fdopen(os.open(staging,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as output:output.write(data)
                            staging.replace(path)
                        finally:staging.unlink(missing_ok=True)
                result=self._capture_source_impl(window,scene_token,index)
                if self.shared_cache:
                    stem=self.shared_cache.stem(window)
                    metadata=json.loads((self.root/(stem+'.json')).read_text())
                    self.shared_cache.publish(window,metadata,(self.root/(stem+'.png')).read_bytes())
                return result
            except Exception:
                # The controller lease cannot own a capture that never returns.
                epoch=self.current_capture_epoch
                if epoch:
                    for prefix in ('','frame-','composed-'):(self.root/(prefix+epoch+'.png')).unlink(missing_ok=True)
                raise
            finally:self.current_capture_epoch=None
    def _capture_source_impl(self,window,scene_token,index):
        with self.capture_lock:
            self.check_current(window)
            target=self.target(window)
            if not target or not target.get('visible'):raise ValueError('actual taskbar icon unavailable')
            icon=target['rect']
            self.capture_serial+=1
            epoch=self.capture_session+'-'+str(self.capture_serial)
            self.current_capture_epoch=epoch
            image=self.root/(epoch+'.png')
            cache=self.root/('full-'+str(window['stableId'])+'-'+str(window['pid']))
            if window.get('workspace',{}).get('name')=='special:win-minimized':
                captured=self.base.capture(window,epoch)
                metadata=json.loads(cache.with_suffix('.json').read_text())
                metadata['rect']=captured['rect']
                image=Path(captured['image'])
            else:
                expression='print(hl.plugin.hyprbars.window_atlas('+','.join((json.dumps(window['address']),json.dumps(str(window['stableId'])),str(window['pid']),json.dumps(str(image)),json.dumps(epoch)))+'))'
                metadata=json.loads(subprocess.check_output(['hyprctl','repl',expression],text=True,timeout=1))
                if (not metadata.get('ok') or not metadata.get('whole') or not metadata.get('canonical') or metadata.get('captureEpoch')!=epoch
                        or str(metadata.get('stableId'))!=str(window['stableId']) or metadata.get('pid')!=window['pid']):
                    image.unlink(missing_ok=True)
                    raise ValueError('canonical exact-identity atlas unavailable: '+str(metadata))
                self.validate_snapshot(metadata,rectangle(window));self.check_current(window)
                metadata.update(identity=list(key(window)),clientSize=list(window['size']))
                self.publish_crop(window,epoch,image,metadata)
                for extension,data in (('.png',image.read_bytes()),('.json',json.dumps(metadata).encode())):
                    staging=self.root/(cache.name+'-'+epoch+extension+'.tmp')
                    with os.fdopen(os.open(staging,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as output:output.write(data)
                    staging.replace(cache.with_suffix(extension))
            self.check_current(window)
            image.chmod(0o600)
            scale=metadata['pixels'][0]/metadata['rect']['width']
            return {'stableId':str(window['stableId']),'pid':int(window['pid']),
                'digest':hashlib.sha256(image.read_bytes()).hexdigest(),'path':str(image),
                'nativeRect':rectangle(window),'atlasRect':metadata['rect'],'iconRect':icon,
                'insets':metadata['insets'],'pixels':metadata['pixels'],'captureScale':scale,
                'captureEpoch':epoch,'sceneToken':scene_token,'targetScreen':target['screenName']}
    def release_sources(self,sources):
        for source in sources:
            path=Path(source.get('path',''))
            if path.parent==self.root and production.re.fullmatch(r'[0-9a-f]{12}-[1-9][0-9]{0,14}\.png',path.name):
                path.unlink(missing_ok=True)
        self.janitor()
