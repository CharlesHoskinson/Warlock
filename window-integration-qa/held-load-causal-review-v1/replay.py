"""Read-only exact Held V6 loader/evaluation attribution; no native command."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,stat
B=Path(__file__).resolve().parent;QA=B.parent
spec=importlib.util.spec_from_file_location('reader',QA/'toolkit-held-terminal-audit-v2/audit.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
S=QA/'toolkit-held-matrix-v6';A=S/'attempt-1';F=A/'qt-wayland'

def main():
 frozen=r.js(S/'frozen-inputs.json');sources={}
 for name,h in frozen['inputs'].items():assert r.digest(name)==(h,frozen['inputModes'][name]),name
 for name,target in frozen['symlinks'].items():assert Path(name).is_symlink() and os.readlink(name)==target,name
 def retain(p):
  p=Path(p);sources[str(p)]=r.digest(p)[0];return r.read(p)
 raw=retain(F/'terminal-helpers/helper-events.jsonl');cfg_raw=retain(F/'terminal-helpers/helper-config.json');archive=r.js(F/'terminal-helpers/archive.json')
 assert hashlib.sha256(raw).hexdigest()==archive['logSHA256'] and hashlib.sha256(cfg_raw).hexdigest()==archive['configSHA256'] and archive['completeEOF']
 events=[json.loads(line) for line in raw.splitlines() if line.strip()];config=json.loads(cfg_raw)
 refused=[dict(line=i,event=e) for i,e in enumerate(events,1) if e['event']=='refused'];assert len(refused)==4
 hydrates=[x for x in refused if x['event']['helper']=='snap'];relay=[x for x in refused if x['event']['helper']=='shell'];assert len(hydrates)==3 and len(relay)==1
 assert all(e['event']['delegateExecuted'] is False and e['event']['exitCode']==125 and e['event']['reason']=='Duplicate or unauthorized helper operation' for e in refused)
 assert all(e['event']['ancestry']==[dict(config['compositor'],start=config['compositor']['start'],parent=config['queryRoots']['harness']['identity']['pid'],pgid=config['compositor']['pid'])] for e in refused)
 assert all(e['event']['operation']=='generation:2:hydrate' for e in hydrates) and relay[0]['event']['operation']=='generation:2:inactive-fileDrag'
 log=re.sub(r'\x1b\[[0-9;]*m','',retain(F/'host/hyprland.log').decode()).splitlines()
 def find(token):return [i+1 for i,line in enumerate(log) if token in line]
 unload=find('[PluginSystem] Plugin hyprbars unloaded.');load=find('[PluginSystem] Plugin hyprbars loaded.')
 born={e['event']['wrapper']['pid']:find('Process created with pid '+str(e['event']['wrapper']['pid']))[0] for e in refused}
 assert unload[0]<born[1919372]<load[1]<born[1919382]<born[1919383]
 assert not any('[lua] file ' in line and 'modified, reloading' in line for line in log)
 config_file=F/'host/runtime-archive/hyprland.lua';retain(config_file)
 variant=r.js(F/'report.json');assert r.digest(config_file)[0]==variant['reloadConfigurationWitness']['sha256']
 core=B/'primary/src_plugins_PluginSystem.cpp';api=B/'primary/src_plugins_PluginAPI.cpp';native=QA/'toolkit-interruption-v6/native-candidate/main.cpp';loop=B/'primary/src_managers_eventLoop_EventLoopManager.cpp';lua=B/'primary/src_config_lua_ConfigManager.cpp'
 for p in (core,api,native,loop,lua,B/'primary/version.h',B/'primary-sources.json',S/'held_route.py',S/'helper_setup.py',S/'helper_observer.py'):retain(p)
 text=core.read_text();assert text.count('g_pEventLoopManager->doLater([] { Config::mgr()->reload(); });')==2
 assert 'HyprlandAPI::reloadConfig();' in native.read_text() and 'g_pEventLoopManager->doLater([] { Config::mgr()->reload(); });' in api.read_text()
 assert 'for (auto& f : fns)' in loop.read_text() and 'f.second();' in loop.read_text()
 case=r.js(F/'case-3/report.json');retain(F/'case-3/report.json');between=r.one(case['trace'],'label','actual native state between unload/reload')['native'];before=r.one(case['trace'],'label','before actual nonrelease interruption')['native'];peer=r.one(case['trace'],'label','separate WM focus intervention')['native']['nativeFocus']
 assert between['coreDragTarget'] is None and r.eq(between['nativeFocus'],peer) and between['signalDownButtonIds']==before['signalDownButtonIds']==[272] and r.groups(before)==r.groups(between)
 assert config['loadGeneration']==2 and 'Refused helper cannot authorize another load' in case['error']
 host=variant['hostEvidence'];unexpected=host['unexpectedInnerDescendants'];probe_unload=find('[PluginSystem] Plugin toolkit_held_probe unloaded.')
 assert any(p['pid']==1919448 and str(p['start'])=='12384516' and p['pgid']==config['compositor']['pid'] and r.gone(p) for p in unexpected)
 late=find('Process created with pid 1919448')[0];assert probe_unload[0]<late
 result=dict(result='actual loader-triggered evaluation authority gap confirmed',sourceManifestSHA256=r.digest(S/'frozen-inputs.json')[0],sourceCount=len(frozen['inputs']),modeCount=len(frozen['inputModes']),linkCount=len(frozen['symlinks']),completeFrozenBytesModesLinks=True,refused=refused,hostLines=dict(firstUnload=unload[0],reloadPlugin=load[1],refusedSpawn=born,finalProbeUnload=probe_unload[0],lateHydrateSpawn=late),nativeUnloadRetirement=dict(exactControllerRetired=True,independentNativeFocusPreserved=True,realRawButtonUnchanged=True,groupsPreserved=True),coreCommit='efb50993780079460b0cbed1363e2166a2de1d9f',expectedAutomaticEvaluations=dict(unload=1,load=2),explicitReloadNotReached=True,watcherReloadMarkerAbsent=True,duplicateProductLuaListenerEstablished=False,allRefusedBeforeDelegate=True,retainedProducerFailure=True,full52Accepted=False,nativeCommands=False,mainWrites=False,sources=sources,boundary='Core control flow comes from advertised clean exact commit and corroborating retained execution log; not a rebuilt core or native callback trace')
 target=A/'root-held-load-causal-replay-v1.json';fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(result,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 print(json.dumps(dict(result=result['result'],artifact=str(target),sha256=r.digest(target)[0])))
if __name__=='__main__':main()
