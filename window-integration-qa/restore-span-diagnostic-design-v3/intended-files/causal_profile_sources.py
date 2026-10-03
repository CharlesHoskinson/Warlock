"""Explicit diagnostic path/qualname selection; no product methods replaced."""
from pathlib import Path

TARGETS={
 'scene_controller':('SceneController.prepare','SceneController.fresh','SceneController.commit_members','SceneController.watchdog','SceneController.settle'),
 'native_desktop':('NativeDesktop.plan_destinations','NativeDesktop.plan_destinations.<locals>.plan','NativeDesktop.plan_destinations.<locals>.guard','NativeDesktop.plan_destination','NativeDesktop.apply_destination','NativeDesktop.refresh_destination','NativeDesktop.capture_source','NativeDesktop._capture_source_impl','NativeDesktop.target','NativeDesktop.retire_gestures','NativeDesktop.finish_capture_previews'),
 'production_motion_6d9':('BasicDesktop.capture','BasicDesktop.clients','BasicDesktop.ipc','BasicDesktop.target','BasicDesktop.reduced','BasicDesktop.monitors','Desktop.capture','Desktop.capture_locked','Desktop.check_current','Desktop.publish_crop'),
 'owned_commands':('OwnedCommands.run','OwnedCommands.check_output'),
 'owned_launch':('OwnedLaunch.__init__','OwnedLaunch.complete'),
 'helper_supervisor':('Keeper.register','Keeper.complete','Keeper.exchange'),
 'readonly_ipc':('ReadonlyIPC.query',),
 'snapshot_cache':('SnapshotCache.restore','SnapshotCache.publish'),
 'batch_preview':('BatchPreviews.stage','BatchPreviews.finish'),
 'pipe_transport':('PipeTransport.ensure_outputs','PipeTransport.send'),
 'service_runtime':('RuntimeService.persist',)}
OBSERVER=('ObservedFactory.retain_source','ObservedFactory.retain_cache_pair','ObservedFactory.__call__.<locals>.capture_and_observe')

def selected_sources(service,service_manifest,observer_path,collector_manifest):
 if sum(map(len,TARGETS.values()))+len(OBSERVER)>64:
  raise ValueError('finite bounded diagnostic selection required')
 result={str(service/(name+'.py')):{
  'sha256':service_manifest['inputs'][str(service/(name+'.py'))],
  'mode':service_manifest['inputModes'][str(service/(name+'.py'))],
  'symbols':list(symbols),
 } for name,symbols in TARGETS.items()}
 observer=str(Path(observer_path).resolve())
 result[observer]={'sha256':collector_manifest['inputs'][observer],
                   'mode':collector_manifest['inputModes'][observer],
                   'symbols':list(OBSERVER)}
 return result
