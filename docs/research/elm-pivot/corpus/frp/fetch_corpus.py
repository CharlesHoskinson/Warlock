from scrapling.fetchers import Fetcher
from pathlib import Path
import hashlib,json,datetime,subprocess
root=Path(__file__).resolve().parent
sources={
'elm-farewell-frp':'https://elm-lang.org/news/farewell-to-frp',
'elm-concurrent-frp-thesis':'https://elm-lang.org/assets/papers/concurrent-frp.pdf',
'fran-1997-index':'https://conal.net/papers/icfp97/',
'fran-1997-paper':'https://conal.net/papers/icfp97/icfp97.pdf',
'push-pull-2009-index':'https://conal.net/papers/push-pull-frp/',
'push-pull-2009-paper':'https://conal.net/papers/push-pull-frp/push-pull-frp.pdf',
'yampa-arrowized-2003':'https://www.cs.yale.edu/homes/external/nilsson/Publications/afp2002.pdf',
'elm-browser-animation-kernel':'https://raw.githubusercontent.com/elm/browser/1.0.2/src/Elm/Kernel/Browser.js',
'elm-browser-events':'https://raw.githubusercontent.com/elm/browser/1.0.2/src/Browser/Events.elm',
'elm-core-platform-kernel':'https://raw.githubusercontent.com/elm/core/1.0.5/src/Elm/Kernel/Platform.js',
'elm-core-command':'https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm',
'elm-core-subscription':'https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Sub.elm',
'elm-ports-guide':'https://guide.elm-lang.org/interop/ports.html',
'qt-bindings-611':'https://doc.qt.io/qt-6.11/qtqml-syntax-propertybinding.html',
'qt-animations-611':'https://doc.qt.io/qt-6.11/qtquick-statesanimations-animations.html',
}
records=[]
for name,url in sources.items():
 try:
  response=Fetcher.get(url);body=response.body;is_pdf=body.startswith(b'%PDF-')
  suffix='.pdf' if is_pdf else '.html' if b'<html' in body[:500].lower() else '.source'
  path=root/(name+suffix);path.write_bytes(body)
  extracted=root/(name+'.txt')
  if is_pdf:subprocess.run(['pdftotext','-layout',str(path),str(extracted)],check=True)
  else:extracted.write_text(response.get_all_text())
  records.append({'name':name,'url':url,'final_url':str(response.url),'status':response.status,'artifact':str(path),'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'extracted':str(extracted),'extracted_sha256':hashlib.sha256(extracted.read_bytes()).hexdigest()})
 except Exception as e:records.append({'name':name,'url':url,'error':str(e)})
(root/'manifest.json').write_text(json.dumps({'fetched_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fetcher':'Scrapling Fetcher','scope':'curated primary sources; not exhaustive FRP literature','sources':records},indent=2)+'\n')
print(json.dumps([{key:row[key] for key in ('name','status','bytes','error') if key in row} for row in records],indent=2))
