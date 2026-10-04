import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path('/home/hoskinson/omarchy-windows-parity');s=Path(__file__).resolve().parents[1];records={};reports=[];datasets=[]
def verify(p,expected=None):
 p=Path(p);data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();assert expected is None or sha==expected,str(p);records[str(p)]={'sha256':sha,'size':len(data)};return sha
for lane,stamp,scale in [('elm-xdg-presented-landmark-native-v212','1791133183538677576',1),('elm-xdg-presented-landmark-buffer2-native-v217','1791133621888297066',2)]:
 p=r/'implementation'/lane/'qa'/('native-'+stamp)/'report.json';reportsha=verify(p);d=json.loads(p.read_text());assert not d['passed'] and d['cleanupPassed'] and len(d['checks'])==60 and d['primaryProfile']==f'origin-scale{scale}' and not d['profileCleanupErrors'] and not d['finalCleanupErrors']
 for name,digest in d['inputs'].items():verify(name,digest)
 for name,digest in d['artifacts'].items():verify(p.parent/name,digest)
 captures=d['pixelCaptures'];assert len(captures)==4 and all(c['passed'] for c in captures[:3]) and not captures[-1]['passed']
 raw=[]
 for c in captures:
  assert c['buffer']['scale']==scale and c['output']['scale']==1 and len(c['samples'])==5 and all(len(row['measured'])==9 for row in c['samples'])
  path=p.parent/'native-evidence'/Path(c['directory']).name/'capture.rgb';verify(path,c['artifacts']['capture.rgb']);raw.append(path.read_bytes())
 datasets.append((captures,raw));reports.append({'path':str(p),'sha256':reportsha,'campaignPassed':False,'cleanupPassed':True,'checksReached':60,'checksPassed':sum(x['passed'] for x in d['checks']),'zeroCapturesPassed':3,'nonzeroCapturePassed':False,'bufferScale':scale})
comparisons=[]
for index,((a,aa),(b,bb)) in enumerate(zip(zip(*datasets[0]),zip(*datasets[1]))):
 assert a['buffer']['ackedSerial']==b['buffer']['ackedSerial'] and a['buffer']['geometry']==b['buffer']['geometry'] and a['native']['at']==b['native']['at'] and a['native']['size']==b['native']['size'] and len(aa)==len(bb)
 comparisons.append({'phaseIndex':index,'selectedSerial':a['buffer']['ackedSerial'],'rgbIdentical':aa==bb,'differentRGBBytes':sum(x!=y for x,y in zip(aa,bb)),'sampleMeasurementsEqual':[x['measured'] for x in a['samples']]==[x['measured'] for x in b['samples']]})
analysis=r/'implementation/elm-xdg-nonzero-presented-failure-v218/failure-manifest.json';verify(analysis)
out=s/'qa'/('verify-'+str(time.time_ns()));out.mkdir();report={'evidenceIntegrityPassed':True,'reports':reports,'bufferScaleComparisons':comparisons,'files':records,'zeroOriginBuffer1And2PresentedSnapshots':6,'nonzeroOriginPresentationAccepted':False,'actualMonitorScale':1,'nativePointerAccepted':False,'hardwareAccepted':False,'fullFourProfileAccepted':False,'fullGeometryAccepted':False,'fullRoadmapAccepted':False,'releaseAccepted':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(f.relative_to(s)):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':f.stat().st_size} for f in sorted(s.rglob('*')) if f.is_file() and f.name!='evidence-manifest.json'};(s/'evidence-manifest.json').write_text(json.dumps({'evidenceIntegrityPassed':True,'fullNativeCampaignAccepted':False,'releaseAccepted':False,'files':files,'externalFiles':records},indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'verifiedFiles':len(records),'comparisons':comparisons}))
