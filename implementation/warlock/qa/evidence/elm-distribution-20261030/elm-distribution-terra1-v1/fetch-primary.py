#!/home/charles/.local/share/uv/tools/scrapling/bin/python
"""Fetch exactly two locked npm packages as opaque bytes; never execute them."""
import datetime,hashlib,json,pathlib
from scrapling.fetchers import Fetcher
P=pathlib.Path(__file__).resolve().parent
L=pathlib.Path('/home/charles/Warlock/implementation/warlock-preview-provider-v143/qa/toolchain/npm-package/package-lock.json')
lock=json.loads(L.read_bytes()); rows=[]
for name,key,meta in [('elm','node_modules/elm','https://registry.npmjs.org/elm/0.19.2-0'),('linux-x64','node_modules/@elm_binaries/linux_x64','https://registry.npmjs.org/@elm_binaries%2Flinux_x64/0.19.2-0')]:
 entry=lock['packages'][key];assert entry['version']=='0.19.2-0'
 for kind,url in [('metadata',meta),('archive',entry['resolved'])]:
  assert url.startswith('https://registry.npmjs.org/')
  r=Fetcher.get(url,headers={'Accept-Encoding':'identity'},follow_redirects=False,timeout=40,retries=0,stealthy_headers=False)
  headers={str(k).lower():('[redacted]' if str(k).lower() in ('set-cookie','authorization','proxy-authorization','cookie') else str(v)) for k,v in r.headers.items()};body=r.body
  if r.status!=200 or headers.get('content-encoding','identity').lower() not in ('identity',''):raise RuntimeError(f'{url}: status={r.status} encoding={headers.get("content-encoding")} location={headers.get("location")}')
  out=P/(name+('.tgz' if kind=='archive' else '.json'));out.write_bytes(body)
  rows.append({'kind':kind,'package':key,'requestedURL':url,'responseURL':str(r.url),'status':r.status,'headers':headers,'retrievedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(body).hexdigest(),'size':len(body),'file':out.name,'redirectPolicy':'disabled','requestAcceptEncoding':'identity'})
(P/'responses.json').write_text(json.dumps({'lockPath':str(L),'lockSHA256':hashlib.sha256(L.read_bytes()).hexdigest(),'responses':rows},indent=2)+'\n')
