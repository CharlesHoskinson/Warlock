"""Generate an unapplied single-module proposal from frozen V28."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
SOURCE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-focus-transaction-v28/native_desktop.py')
METHOD='''    def _capture_hidden_fused(self,window,epoch):
        # Owned hidden path only. Frozen standalone capture remains unchanged.
        if type(self.commands) is not OwnedCommands or type(self.preview_batch) is not BatchPreviews:
            raise ValueError('canonical owned hidden capture required')
        with self.base.snapshot_lock:
            native=rectangle(window);image=self.root/(epoch+'.png')
            cache=self.root/('full-'+str(window['stableId'])+'-'+str(window['pid']))
            frame=cache.with_suffix('.png');metadata_path=cache.with_suffix('.json')
            metadata=json.loads(metadata_path.read_text())
            if not isinstance(metadata,dict) or metadata.get('identity')!=list(key(window)) or metadata.get('clientSize')!=[native['width'],native['height']] or not metadata.get('whole') or not frame.is_file():
                raise ValueError('no matching whole-window cache')
            self.base.validate_snapshot(metadata)
            self.base.check_current(window)
            insets=metadata['insets']
            full={'x':native['x']-insets['left'],'y':native['y']-insets['top'],'width':native['width']+insets['left']+insets['right'],'height':native['height']+insets['top']+insets['bottom']}
            preview=self.production.RUNTIME/'hypr-window-previews'
            temporary=preview/('.motion-'+epoch+'.png')
            composed=self.root/('composed-'+epoch+'.png')
            closed=False
            try:
                self.commands.run(['grim','-T',str(window['stableId']),str(image)],check=True,
                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=.65)
                if not image.is_file() or image.stat().st_size<64:
                    raise ValueError('empty toplevel snapshot')
                preview.mkdir(mode=0o700,parents=True,exist_ok=True)
                with (preview/(window['address']+'.lock')).open('w') as lock:
                    self.production.fcntl.flock(lock,self.production.fcntl.LOCK_EX)
                    if not any(key(current)==key(window) for current in self.base.clients()):
                        raise ValueError('identity changed during capture')
                    # Former post-thumbnail observation moves BEFORE the one
                    # helper. Raw pixels and frame composition stay distinct.
                    self.base.check_current(window)
                    scale=metadata['pixels'][0]/full['width'];x=round(insets['left']*scale);y=round(insets['top']*scale)
                    self.commands.run(['magick','-respect-parentheses',
                        '(',str(image),'-thumbnail','300x180>','-write',str(temporary),'+delete',')',
                        str(frame),'(',str(image),'-resize',str(round(native['width']*scale))+'x'+str(round(native['height']*scale))+'!',')',
                        '-geometry','+'+str(x)+'+'+str(y),'-compose','SrcAtop','-composite',str(composed)],
                        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=1)
                    # OwnedCommands normal return includes genuine group
                    # closure. Preserve the original post-compose observation.
                    closed=True
                    self.base.check_current(window)
                    for slot in (0,1):
                        output=preview/(window['address']+'-'+str(slot)+'.png')
                        staging=output.with_suffix('.motion.tmp')
                        staging.write_bytes(temporary.read_bytes());staging.replace(output)
                    destination=preview/(window['address']+'.json')
                    staging=destination.with_suffix('.motion.tmp')
                    staging.write_text(json.dumps({'pid':window['pid'],'stableId':window['stableId']},separators=(',',':'))+'\\n')
                    staging.replace(destination)
                    composed.replace(image)
                return {'image':str(image),'rect':full,'whole':True}
            except BaseException:
                try:closed=self.preview_batch._closed()
                except BaseException:closed=False
                if not closed:
                    # Exact epoch cannot be discarded while owned helper
                    # completion is unknown, even after its leader disappears.
                    with self.preview_batch.lock:
                        self.preview_batch.quarantined=True
                        self.preview_batch.active_epochs.add(epoch)
                raise
            finally:
                if closed:
                    temporary.unlink(missing_ok=True);composed.unlink(missing_ok=True)
'''

def stamp(path):return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':stat.S_IMODE(path.stat().st_mode)}
def save(path,data):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:f.write(data)

def main():
    formal=json.loads((HERE/'formal-complete.json').read_text());assert formal['result']=='pass' and formal['named']==18
    pixel=json.loads((HERE/'pixel-replay.json').read_text());assert pixel['result']=='pass' and len(pixel['cases'])==16
    before=SOURCE.read_text();old='                captured=self.base.capture(window,epoch)\n'
    new='                captured=self._capture_hidden_fused(window,epoch) if type(self.commands) is OwnedCommands and type(self.preview_batch) is BatchPreviews else self.base.capture(window,epoch)\n'
    assert before.count(old)==1
    anchor='    def _capture_source_impl(self,window,scene_token,index):\n';assert before.count(anchor)==1
    after=before.replace(anchor,METHOD+anchor).replace(old,new)
    assert after.replace(METHOD,'').replace(new,old)==before
    ast.parse(after)
    target=HERE/'native_desktop.py.proposed';save(target,after)
    patch=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=str(SOURCE),tofile='fresh-V29/native_desktop.py'))
    save(HERE/'intended.patch',patch)
    save(HERE/'intended-source-map.json',json.dumps({'result':'pass','original':{'path':str(SOURCE),**stamp(SOURCE)},'proposed':{'path':str(target),**stamp(target)},'patch':stamp(HERE/'intended.patch'),'completeInverseExact':True,'inheritedChangedMethods':['_capture_source_impl'],'newMethods':['_capture_hidden_fused'],'productionMotionUnchanged':True,'sceneControllerUnchanged':True,'batchPreviewsUnchanged':True,'ownedCommandsUnchanged':True,'applied':False},indent=2)+'\n')
    print(json.dumps({'result':'pass','patchSHA256':stamp(HERE/'intended.patch')['sha256'],'applied':False}))

if __name__=='__main__':main()
