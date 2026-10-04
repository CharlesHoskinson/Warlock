"""Characterize immutable ancestor versus live environment; never repair/retarget it."""
import hashlib,json,os,pathlib,time
ROOT=pathlib.Path(__file__).resolve().parents[1];BASE=ROOT.parent/'elm-qt6-full-driver-surface-transform-v313';out=ROOT/'qa'/('drift-'+str(time.time_ns()));out.mkdir()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
packet=json.loads((BASE/'component-manifest.json').read_text());different=[];verified=0
for name,row in packet['externalFiles'].items():
 p=pathlib.Path(name);row={'sha256':row} if type(row) is str else row
 try:
  if name.endswith('#symlink'):
   p=pathlib.Path(name[:-8]);value={'symlink':os.readlink(p),'resolved':str(p.resolve(strict=True))};same=value==row
  elif 'symlink' in row:
   value={'symlink':os.readlink(p)};same=value['symlink']==row['symlink']
  else:value={'sha256':sha(p),'size':p.stat().st_size};same=value['sha256']==row['sha256']
  if not same:different.append({'path':name,'expected':row,'actual':value})
  else:verified+=1
 except BaseException as e:different.append({'path':name,'expected':row,'error':repr(e)})
report={'passed':True,'characterizationOnly':True,'upstreamLiveClosurePassed':not different,'nativeAcceptance':False,'verifiedUnchanged':verified,'drift':different,'ancestorManifestSHA256':sha(BASE/'component-manifest.json')}
(out/'drift.py').write_bytes(pathlib.Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'unchanged':verified,'driftCount':len(different),'paths':[r['path'] for r in different]}))
