"""Same original native two-MAX journey plus committed scene/hit receipts.

No fixture, owning tuple, input cadence or deadline changes. Read-only snapshots
must bind to the exact native session. Pointer traversal receipts are correlated
with actual GTK clicks; button-time races/AT/independent acceptance stay separate.
"""
import hashlib,pathlib,sys
assert not sys.argv[1:]
p=pathlib.Path(__file__).with_name('native-max-input-region.py');source=p.read_text()
needle='    def events():\n';assert source.count(needle)==1
source=source.replace(needle,'''    scene_request=30000
    def scene_packet():
     global scene_request
     scene_request+=1
     request=str(scene_request)
     response=client.request({'protocolVersion':3,'kind':'committed-scene-request','binding':client.bound,'requestId':request,'minimumWatermark':'0'})
     check('AuthenticatedCommittedSceneRead',response.get('kind')=='committed-scene' and response.get('sceneProtocol')==1 and response.get('binding')==client.bound and response.get('requestId')==request,response=response)
     return response['observations']
    def ready_scene():
     packet=scene_packet()
     return next((scene for scene in packet['scenes'] if scene['ready'] and scene['outputCommitted'] and primary in scene['order'] and peer in scene['order']),None)
'''+needle)
needle="     before_facts=facts();image=OUTPUT/(name+'.png');helper(['/usr/bin/grim',str(image)])";assert source.count(needle)==1
source=source.replace(needle,"     committed=wait(ready_scene);before_packet=scene_packet();before_hit=max([int(hit['sequence']) for hit in before_packet['hits']] or [0])\n"+needle)
needle="     check(name+'PreservesBothMaxGeometry',";assert source.count(needle)==1
addition='''     released=wait(lambda:[event for event in events() if event['kind']=='released'] if len([event for event in events() if event['kind']=='released'])==before+1 else None)
     check(name+'DeliveredPressRetainsReleaseOwner',released[-1]['window']==expected,released=released[-1],pressed=pressed[-1])
     observed=scene_packet()
     receipts=[hit for hit in observed['hits'] if int(hit['sequence'])>before_hit and hit['ready'] and hit['sceneRevision']==committed['sceneRevision'] and hit['recipient']==labels[expected] and hit['point']==[x,y]]
     check(name+'ConsumesCommittedPaintScene',bool(receipts),paintScene=committed,hitReceipts=receipts,after=observed)
     report.setdefault('committedMaxReceipts',[]).append({'name':name,'paintScene':committed,'hitReceipts':receipts,'observationsAfter':observed,'actualGTKPressed':pressed[-1]})
'''
source=source.replace(needle,addition+needle)
source=source.replace("'native-max-input-region-' if FOCUS", "'native-committed-max-' if FOCUS")
source=source.replace("    report['committedSceneAgreementAccepted']=False", "    report['nativeCommittedMaxSceneObserved']=True\n    report['committedSceneAgreementAccepted']=False")
# Keep the original source and its recorded adaptation intact; this runner is
# a separate source-bound observation of the same original acceptance journey.
exec(compile(source,str(p),'exec'),globals())
