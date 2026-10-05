"""Inert exact new307/319/315 build tuple; no compositor or plugin load."""
import hashlib,json,os,pathlib,re,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
PINS={
 'elm-own-popup-xdg-grab-provenance-v307':'335b15fb98e6276d55d011ceecf6450c9a81e19df2ef72db97377698b8029a13',
 'elm-own-popup-owning-authority-v319':'b67d280ecf9ce823e3cd4bb782ecb2b563a5643cf7ea902859fa03f48c607031',
 'elm-own-popup-native-grab-join-v315':'e89897fcd85478caa182957abf09a8be1f2cd9d661a985111c54aa5c6565c705',
 'elm-own-popup-core-source-review-v317':'ba95ea7efd9b1f17456d8fbd3fbacec54179ee5f3ce6585ad07c3ba7a0dac11f',
 'elm-own-popup-grab-join-review-v318':'83ad6ea17f9f980ea8ed23a1d7706157ee39472affe1639bdb374153f131232f',
 'elm-own-popup-authority-source-review-v320':'24ee2591e728a6f28782ac38503bc8011eb4347d2df04b4d7ce34397c0a97a51',
 'elm-parent-keyboard-canonical-observer-v247':'ea7dc366dda3ab5d7a9ec5efb5c3984915a585673a7da10372fafaf76c45a3f5'}
class Refused(ValueError):pass
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def require(condition,reason):
 if not condition:raise Refused(reason)
def entry(path,data,inventory):
 path=pathlib.Path(path)
 if type(data) is str:data={'sha256':data}
 require(type(data) is dict,'inventory row')
 if 'symlink' in data:
  require(path.is_symlink() and os.readlink(path)==data['symlink'],'symlink changed '+str(path));inventory[str(path)]={'symlink':data['symlink']};return
 require(path.is_file() and sha(path)==data['sha256'],'input changed '+str(path))
 if 'size' in data:require(path.stat().st_size==data['size'],'size changed '+str(path))
 inventory[str(path)]={'sha256':sha(path),'size':path.stat().st_size}
def manifest(name,pin,inventory):
 base=REPO/'implementation'/name;p=base/'component-manifest.json';entry(p,pin,inventory);v=json.loads(p.read_text());require(v['sourceHeld'] is True and v['evidenceIntegrityPassed'] is True,'unheld upstream '+name)
 for rel,row in v['files'].items():
  require(not pathlib.Path(rel).is_absolute() and '..' not in pathlib.Path(rel).parts,'relative source containment');entry(base/rel,row,inventory)
 for section in ('externalFiles','external'):
  for path,row in v.get(section,{}).items():entry(path,row,inventory)
 for rel,row in v.get('symlinks',{}).items():entry(base/rel,{'symlink':row} if type(row) is str else row,inventory)
 return v

def check_pair(core,authority,observer):
 require(core.get('passed') is True and authority.get('passed') is True and observer.get('passed') is True,'actual build refusal')
 headers=core.get('owningHeaders');require(type(headers) is dict and len(headers)==694,'694 owning headers')
 require(headers==authority.get('owningHeaders')==observer.get('owningHeaders'),'owning header mismatch')
 require(len(core.get('translationUnits',[]))==19 and len(core.get('rebuiltArchiveMembers',{}))==19 and core.get('unchangedArchiveMembers')==414,'19/414 archive lineage')
 require(headers.get('src/version.h')==core.get('owningVersionHeaderSHA256'),'owning version mismatch')
 for module in (authority,observer):
  binding=module.get('core',{});require(binding.get('path')==core.get('binary') and binding.get('sha256')==core.get('binarySHA256'),'actual307 core pairing')
  require(type(module.get('strongUndefinedCount')) is int and module['strongUndefinedCount']>0 and module.get('missingSymbols')==[],'strong symbol closure')
 return hashlib.sha256(json.dumps(headers,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def assemble():
 inventory={};held={name:manifest(name,pin,inventory) for name,pin in PINS.items()}
 core_path=pathlib.Path(held['elm-own-popup-xdg-grab-provenance-v307']['buildReport']);authority_path=pathlib.Path(held['elm-own-popup-owning-authority-v319']['buildReport']);observer_path=pathlib.Path(held['elm-own-popup-native-grab-join-v315']['buildReport'])
 packets=[json.loads(p.read_text()) for p in (core_path,authority_path,observer_path)];core,authority,observer=packets;header_digest=check_pair(*packets)
 require(held['elm-own-popup-core-source-review-v317']['ownerManifestSHA256']==PINS['elm-own-popup-xdg-grab-provenance-v307'],'317 owner')
 require(held['elm-own-popup-authority-source-review-v320']['ownerManifestSHA256']==PINS['elm-own-popup-owning-authority-v319'],'320 owner')
 require(held['elm-own-popup-grab-join-review-v318']['sourceManifestSHA256']==PINS['elm-own-popup-native-grab-join-v315'] and held['elm-own-popup-grab-join-review-v318']['coreManifestSHA256']==PINS['elm-own-popup-xdg-grab-provenance-v307'],'318 owner/core')
 for path,packet in zip((core_path,authority_path,observer_path),packets):
  entry(packet['binary'],packet['binarySHA256'],inventory)
  for rel,digest in packet['owningHeaders'].items():entry(path.parent/'owning-headers'/rel,digest,inventory)
  for section in ('dependencies','linkDependencies','linkedLibraries','tools'):
   for p,digest in packet.get(section,{}).items():entry(p,digest,inventory)
  for rel,digest in packet.get('artifacts',{}).items():entry(path.parent/rel,digest,inventory)
 for module in (authority,observer):require(module['core']['buildReport']==str(core_path) and module['core']['buildReportSHA256']==sha(core_path),'explicit307 report')
 cleanup=json.loads((ROOT/'cleanup-origin.json').read_text());base=pathlib.Path(cleanup['ancestor']);entry(base/'component-manifest.json',cleanup['manifestSHA256'],inventory);rows=json.loads((base/'component-manifest.json').read_text())['files']
 for name,digest in {**cleanup['modules'],**cleanup['supportConsumers']}.items():
  require(rows['qa/'+name]['sha256']==digest,'282 retained source pin');entry(base/'qa'/name,digest,inventory);entry(ROOT/'qa/helpers'/name,digest,inventory)
 # Cleanup source is retained exactly; historical282 external/runtime qualification is not transferred.
 aq=json.loads((ROOT/'runtime/aq-tuple.json').read_text());entry(aq['manifest'],aq['manifestSHA256'],inventory);aq_packet=json.loads(pathlib.Path(aq['manifest']).read_text());require(aq_packet['passed'] is True,'AQ155 qualified component')
 for row in aq_packet['files']:entry(pathlib.Path(aq['manifest']).parent/row['path'],row,inventory)
 entry(aq['library'],aq['librarySHA256'],inventory)
 probe=json.loads((ROOT/'runtime/parent-probe-build.json').read_text());entry(probe['buildReport'],probe['buildReportSHA256'],inventory);probe_packet=json.loads(pathlib.Path(probe['buildReport']).read_text());require(probe_packet['passed'] is True,'parent247 actual build')
 for p,digest in probe_packet['owningFiles'].items():entry(p,digest,inventory)
 for field in ('module','client'):entry(probe_packet[field],probe_packet[field+'SHA256'],inventory)
 descriptor={'result':'pass','binary':core['binary'],'sha256':core['binarySHA256'],'buildReport':str(core_path),'buildReportSHA256':sha(core_path),'nativeAcceptance':False,'installed':False,'scope':'Exact307 core +unchanged authority319 and diagnostic observer315; compile/ABI closure only, no own-popup grant or GUI acceptance.','owningHeaderCount':694,'owningHeaderTreeSHA256':header_digest,'owningVersionHeaderSHA256':core['owningVersionHeaderSHA256'],'plugin':{'path':authority['binary'],'sha256':authority['binarySHA256']},'pluginBuildReport':str(authority_path),'pluginBuildReportSHA256':sha(authority_path),'coreComponentManifest':str(core_path.parents[1]/'component-manifest.json'),'coreComponentManifestSHA256':PINS['elm-own-popup-xdg-grab-provenance-v307'],'observer':{'path':observer['binary'],'sha256':observer['binarySHA256'],'buildReport':str(observer_path),'buildReportSHA256':sha(observer_path)},'reviews':{k:v for k,v in PINS.items() if 'review' in k}}
 return descriptor,packets,inventory,aq
