"""Token/source checks and one batch of private headless browser captures."""
import hashlib,json,pathlib,sys,resource,subprocess,time,threading,http.server,os
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[2];OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':scope,'checks':[],'nativeAcceptance':False,'fullReleaseAccepted':False};server=None
inputs={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and 'qa' not in p.relative_to(ROOT).parts}
def check(name,condition):
 assert condition,name
 report['checks'].append(name)
def luminance(color):
 channels=[int(color[i:i+2],16)/255 for i in [1,3,5]];r,g,b=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in channels];return .2126*r+.7152*g+.0722*b
try:
 registry=json.loads((ROOT/'registry.json').read_text());tokens=json.loads((ROOT/'tokens.json').read_text());original=REPO/'DesignLanguage/research/v1/consensus-inputs/implementation/warlock-preview-provider-v1'
 check('49 exact source modules',len(registry['modules'])==49 and all(sha(ROOT/r['file'])==r['sha256']==sha(original/r['file']) for r in registry['modules']))
 check('14 component families cover all 17 rendered and surface wrapper classes',len(registry['components'])==14 and len(registry['renderedClasses'])==17 and set(registry['renderedClasses'])<={s[1:] for c in registry['components'] for s in c['selectors'] if s.startswith('.')})
 check('Source assets and native fallback frozen by hash',all(sha(ROOT/r['file'])==r['sha256'] for r in registry['assets']))
 check('Reference palette identity retained',tokens['brandReferenceSHA256']==sha(REPO/'docs/warlock-brand/v1/tokens.json'))
 for theme,palette in tokens['reference'].items():
  for pair in tokens['pairs']:
   a,b=sorted([luminance(palette[pair['foreground']]),luminance(palette[pair['background']])]);ratio=(b+.05)/(a+.05)
   check(f"{theme}: {pair['foreground']}/{pair['background']} >= {pair['minimum']} ({ratio:.3f})",ratio>=pair['minimum'])
 check('Semantic/component references all resolve',all(v in tokens['reference']['dark'] for v in tokens['semantic'].values()) and all(v in tokens['semantic'] for v in tokens['component'].values()))
 art=ROOT/'assets/art/warlock-flow-wallpaper.png';check('Original artwork bytes reused',sha(art)==sha(REPO/'docs/warlock-brand/v1/art/warlock-flow-wallpaper.png'))
 builds=[json.loads(p.read_text()) for p in (ROOT/'qa').glob('build-*/report.json')];check('Served Elm artifact exactly matches accepted pinned compile',any(b['passed'] and b['artifactSHA256']==sha(ROOT/'assets/design-demo.js') for b in builds))
 class Handler(http.server.SimpleHTTPRequestHandler):
  def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
  def log_message(self,*args):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 browser=pathlib.Path('/home/hoskinson/.cache/puppeteer/chrome-headless-shell/linux-154.0.8037.57/chrome-headless-shell-linux64/chrome-headless-shell');report['browserBinarySHA256']=sha(browser)
 command=['node',str(ROOT/'qa/browser.mjs'),f'http://127.0.0.1:{server.server_port}',str(OUT),str(browser)]
 p=subprocess.run(command,capture_output=True,text=True,timeout=90);(OUT/'helper.stdout').write_text(p.stdout);(OUT/'helper.stderr').write_text(p.stderr)
 check('Browser child normal exit',p.returncode==0);browser_report=json.loads((OUT/'browser-report.json').read_text());check('Batch browser behavior checks',browser_report['passed'] and browser_report['browserExitCode']==0);report['browserReport']=str(OUT/'browser-report.json')
 check('Inputs unchanged during checks',all(sha(ROOT/rel)==value for rel,value in inputs.items()));report['inputs']=inputs;report['passed']=True
except Exception as error:report['error']=repr(error)
finally:
 if server:server.shutdown();server.server_close()
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
