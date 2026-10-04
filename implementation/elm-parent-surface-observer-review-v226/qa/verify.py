import hashlib,json,resource,sys,time,xml.etree.ElementTree as E
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parents[1];owner=root.parent/'elm-parent-surface-observer-v225'
expected=sys.argv[1];manifest=owner/'component-manifest.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(manifest)==expected
rows={}
def add(p,digest=None,size=None):
 assert p.is_file() and not p.is_symlink(),str(p)
 data=p.read_bytes();actual=hashlib.sha256(data).hexdigest()
 if digest:assert actual==digest,str(p)
 if size is not None:assert len(data)==size,str(p)
 rows[str(p)]={'sha256':actual,'size':len(data)}
add(manifest)
for rel,row in json.loads(manifest.read_text())['files'].items():add(owner/rel,row['sha256'],row['size'])
a=E.parse(owner/'original/parent-input.xml').getroot().find('interface')
b=E.parse(owner/'native/parent-input.xml').getroot().find('interface')
a.tail=b.tail=None
assert E.tostring(a)==E.tostring(b),'Original input interface changed'
module=(owner/'native/parent-input-module.c').read_text();header=(owner/'native/surface-observer.h').read_text()
assert 'chosen->current_mode->width < 1' in header and 'chosen->current_mode->height < 1' in header
query=header[header.index('static bool observation_packet'):header.index('static void observe_request')]
for forbidden in ['notify_motion','notify_button','notify_pointer','weston_view_update_transform','weston_pointer_set_focus']:assert forbidden not in query,forbidden
assert 'weston_coord_surface_to_global(selected, weston_coord_surface' in query
for name in ['release_all','resource_destroyed','destroy_request','valid_point','motion_request','button_request','pointer_capability_request','pointer_burst_request','bind_probe','seat_destroyed']:
 def extract(text):
  import re
  match=re.search(r'^static [^\n]*\b'+name+r'\([^\n]*\) \{',text,re.M);assert match,name
  begin=match.start();pos=match.end();depth=1
  while depth:
   if text[pos]=='{':depth+=1
   if text[pos]=='}':depth-=1
   pos+=1
  return text[begin:pos]
 assert extract(module)==extract((owner/'original/parent-input-module.c').read_text()),name
for p in root.rglob('*'):
 if p.is_file() and p.name not in ('component-manifest.json','reviewed-inputs.json'):add(p)
out=root/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
report={'passed':True,'nativeAcceptance':False,'scope':'Read-only held source/interface identity and query-path review, no GUI','files':rows,'checks':len(rows),'heldOwnerManifest':expected}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(root/'reviewed-inputs.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(rows),'report':str(out/'report.json')}))
