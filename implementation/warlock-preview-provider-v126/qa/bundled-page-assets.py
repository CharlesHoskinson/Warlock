"""Require every bundled page script/style in the exact package and allowlist."""
import json,pathlib,re,sys
from html.parser import HTMLParser
assets=pathlib.Path('assets');source=pathlib.Path('native/host.c').read_text()
body=source[source.index('static const char *asset_name('):source.index('/* Observation carrier only.')]
match=re.search(r'static const char \*names\[\]\s*=\s*\{([^}]+)\}',body);assert match
allowed=set(re.findall(r'"([a-z0-9.-]+)"',match.group(1)));assert allowed
class References(HTMLParser):
 def __init__(self):super().__init__();self.names=[]
 def handle_starttag(self,tag,attrs):
  data=dict(attrs)
  if tag=='script' and 'src' in data:self.names.append(data['src'])
  if tag=='link' and data.get('rel')=='stylesheet':self.names.append(data.get('href',''))
pages={}
for page in sorted(assets.glob('*.html')):
 parser=References();parser.feed(page.read_text());assert parser.names,page
 for name in parser.names:
  assert re.fullmatch('[a-z0-9.-]+',name),(page,name,'Closed local bundle reference')
  assert name in allowed,(page,name,'Absent from actual owning scheme allowlist')
  path=assets/name;assert path.is_file() and not path.is_symlink() and 0<path.stat().st_size<=4*1024*1024,(page,name,'Missing or invalid actual compiled page asset')
 pages[page.name]=parser.names
assert 'native-visual-renderer.js' in pages['controlled-popup.html']
assert 'native-preview-admission.js' in pages['controlled-popup.html']
print(json.dumps({'passed':True,'pages':pages,'references':sum(map(len,pages.values())),'nativeAcceptance':False,'fullReleaseAccepted':False}))
