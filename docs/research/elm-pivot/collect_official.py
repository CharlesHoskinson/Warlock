"""Download official Elm guide and every indexed elm/elm-explorations API version with Scrapling."""
import concurrent.futures,datetime,hashlib,json,logging,re,time
from pathlib import Path
from urllib.parse import urljoin,urlsplit,urlunsplit
from scrapling.fetchers import Fetcher
from markdownify import markdownify
ROOT=Path('/home/hoskinson/.cache/windows-parity-research/elm-pivot/official')
ROOT.mkdir(parents=True,exist_ok=True)
rows=[];failed=[]
def digest(data):return hashlib.sha256(data).hexdigest()
def declaration(group,item):
 name=item['name'];args=' '.join(item.get('args',[]));head=name+(' '+args if args else '')
 if group=='aliases':return 'type alias '+head+' =\n    '+item['type']
 if group=='unions':
  cases=[]
  for constructor,arguments in item.get('cases',[]):
   cases.append(constructor+''.join(' ('+argument+')' for argument in arguments))
  if not cases:return '-- Opaque type: '+head+' (constructors not exposed)'
  return 'type '+head+'\n    = '+'\n    | '.join(cases)
 return ('('+name+')' if group=='binops' else name)+' : '+item['type']
def fetch(url,kind,key,expect=None):
 dest=ROOT/key;dest.parent.mkdir(parents=True,exist_ok=True)
 try:
  response=Fetcher.get(url,timeout=25,retries=1)
  body=response.body
  row={'url':url,'resolvedUrl':str(response.url),'status':response.status,'kind':kind,'bytes':len(body),'sha256':digest(body),'raw':str(dest),'fetchedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  dest.write_bytes(body)
  if response.status!=200:raise ValueError('HTTP '+str(response.status))
  value=json.loads(body) if expect in ('json','docs') else None
  if expect=='docs' and not isinstance(value,list):raise ValueError('Expected module documentation array')
  if expect=='docs':
   docs=['# '+key,'Source: '+url,'']
   for module in value:
    docs+=['# '+module['name'],'',module.get('comment',''),'']
    for group in ('aliases','unions','values','binops'):
     for item in module.get(group,[]):
      docs+=['## '+item['name'],'','```elm',declaration(group,item),'```','',item.get('comment',''),'']
   md=dest.with_suffix('.md');md.write_text('\n'.join(docs));row.update(modules=len(value),markdown=str(md),markdownSHA256=digest(md.read_bytes()))
  elif expect is None and kind in ('guide','reference'):
   content=response.css('section.normal').get()
   if not content:content=body.decode('utf-8',errors='replace')
   md=dest.with_suffix('.md');md.write_text('# Source: '+url+'\n\n'+markdownify(content));row.update(markdown=str(md),markdownSHA256=digest(md.read_bytes()),extractedCharacters=len(response.get_all_text()))
  return row,response,value
 except Exception as e:
  return {'url':url,'kind':kind,'raw':str(dest),'error':repr(e)},None,None

def save():
 manifest={'collector':'Scrapling Fetcher.get; raw bytes retained; API JSON decoded and guide Markdown extracted','scope':'Complete reachable English official guide + all indexed versions of elm/* and elm-explorations/* package README, elm.json and docs.json. Excludes third-party ecosystem and translations; historical official signals documentation handled separately.','entries':sorted(rows,key=lambda r:r['url']),'failures':failed}
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
queue=['https://guide.elm-lang.org/'];seen=set()
while queue:
 url=queue.pop(0)
 parsed=urlsplit(url);url=urlunsplit((parsed.scheme,parsed.netloc,parsed.path,'',''))
 if url in seen:continue
 seen.add(url)
 if len(seen)>200:raise RuntimeError('Guide exceeds expected bound; inspect scope before continuing')
 key='guide/'+(parsed.path.strip('/') or 'index')
 if not key.endswith('.html'):key+='.html'
 row,response,_=fetch(url,'guide',key)
 if response is None:failed.append(row);continue
 rows.append(row)
 for href in response.css('a::attr(href)').getall():
  target=urljoin(url,href);p=urlsplit(target)
  if p.netloc=='guide.elm-lang.org' and p.scheme=='https' and not p.query and not re.search(r'\.(?:png|jpg|svg|css|js|pdf|woff|ico)$',p.path) and '/assets/' not in p.path:
   target=urlunsplit((p.scheme,p.netloc,p.path,'',''))
   if target not in seen:queue.append(target)
 save()
row,_,index=fetch('https://package.elm-lang.org/all-packages','package-index','all-packages.json','json')
if index is None:failed.append(row);save();raise RuntimeError('Official package index unavailable')
rows.append(row)
packages={k:v for k,v in index.items() if k.startswith(('elm/','elm-explorations/'))}
(ROOT/'official-package-versions.json').write_text(json.dumps(packages,indent=2)+'\n')
requests=[]
for package,versions in packages.items():
 for version in versions:
  for filename,expect in [('docs.json','docs'),('elm.json','json'),('README.md',None)]:
   requests.append(('https://package.elm-lang.org/packages/'+package+'/'+version+'/'+filename,'package-api' if expect=='docs' else 'package-metadata','packages/'+package+'/'+version+'/'+filename,expect))
print(json.dumps({'guidePages':len(rows)-1,'packages':len(packages),'versions':sum(map(len,packages.values())),'packageRequests':len(requests)}),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
 futures=[executor.submit(fetch,*request) for request in requests]
 for future in concurrent.futures.as_completed(futures):
  row,_,_=future.result()
  (failed if 'error' in row else rows).append(row)
  save()
summary={'guidePages':sum(r['kind']=='guide' for r in rows),'officialPackages':len(packages),'officialPackageVersions':sum(map(len,packages.values())),'apiVersions':sum(r['kind']=='package-api' for r in rows),'moduleVersions':sum(r.get('modules',0) for r in rows),'successfulDownloads':len(rows),'failures':len(failed),'manifest':str(ROOT/'manifest.json')}
(ROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
