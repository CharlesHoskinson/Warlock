import hashlib,http.server,json,pathlib,re,resource,subprocess,sys,threading,time,urllib.parse
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
out=root/('.warlock-contributor/documentation-browser-'+str(time.time_ns()));out.mkdir(exist_ok=False)
docs=['README.md','CONTRIBUTING.md','DesignLanguage/README.md','DesignLanguage/WORKPLAN.md','DesignLanguage/CURRENT.md','DesignLanguage/CONTRIBUTING.md','DesignLanguage/DESIGN.md','DesignLanguage/PRODUCT.md','DesignLanguage/INTERACTION-ADDENDUM.md','DesignLanguage/catalog/WORKPLAN.md','DesignLanguage/catalog/index.html','DesignLanguage/current.css','plugins/warlock-contributor/README.md','plugins/warlock-contributor/references/implementation.md','docs/warlock-roadmap/FEATURE-COMPLETION.md','implementation/warlock/README.md']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={p:sha(root/p) for p in docs}
report={'passed':False,'scope':scope,'checks':[],'inputs':inputs,'nativeAcceptance':False,'fullReleaseAccepted':False}
def check(name,ok):
    assert ok,name
    report['checks'].append(name)
server=None
try:
    links=0
    for name in docs:
        p=root/name;text=p.read_text()
        targets=re.findall(r'\[[^\]]*\]\(([^)]+)\)',text) if p.suffix=='.md' else re.findall(r'(?:href|src)="([^"]+)"',text) if p.suffix=='.html' else re.findall(r'url\("?([^"\)]+)',text)
        for target in targets:
            if '://' in target or target.startswith(('#','mailto:')):continue
            target=urllib.parse.unquote(target.split('#',1)[0].split('?',1)[0])
            check('Link resolves: '+name+' → '+target,(p.parent/target).exists());links+=1
    report['resolvedLocalLinks']=links
    # Existing versioned specimen bytes must remain frozen.
    check('Frozen v6 unchanged',not subprocess.check_output(['git','diff','--name-only','HEAD','--','DesignLanguage/catalog/v6'],cwd=root).strip())
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*a,**k):super().__init__(*a,directory=str(root),**k)
        def log_message(self,*a):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
    inherited=(root/'DesignLanguage/catalog/v6/qa/browser.mjs').read_text()
    prefix=inherited[:inherited.index('try{\n let match;')]
    setup=inherited[inherited.index(' let match;'):inherited.index(" await call('Page.enable');")]
    suffix=inherited[inherited.index('}catch(error){report.error='):]
    body=r'''
 await call('Page.enable');await call('Runtime.enable');await call('Log.enable');await call('Network.enable');
 await viewport(1440);await call('Page.navigate',{url:base+'/DesignLanguage/catalog/index.html'});await until('!!document.querySelector("#contributors")');await evaluate('document.fonts.ready');
 check('Current heading and plugin section',await evaluate('document.querySelectorAll("h1").length===1 && document.querySelector("#contributors").textContent.includes("Claude Code, Codex and Grok")'));
 check('Development and fixture scope visible',await evaluate('document.body.textContent.includes("14 component families") && document.body.textContent.includes("incomplete") && document.body.textContent.includes("simulated native outcomes")'));
 check('Approved tokens render',await evaluate('getComputedStyle(document.body).backgroundColor==="rgb(16, 17, 26)"'));
 check('Font loaded',await evaluate('document.fonts.check("16px Inter")'));
 const links=await evaluate('[...document.querySelectorAll("a[href]")].map(a=>a.href)');
 for(const url of [...new Set(links)]){const r=await fetch(url);check('Browser link HTTP '+url,r.status===200);}
 await capture('current-catalog-desktop');
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
 check('Keyboard skip link reachable',await evaluate('document.activeElement.className==="skip"'));
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await sleep(80);
 check('Skip reaches main',await evaluate('location.hash==="#main" && document.activeElement.id==="main"'));
 for(const width of [1440,390,320]){await viewport(width);check('No horizontal page overflow '+width,await evaluate('document.documentElement.scrollWidth<=innerWidth'));}
 await capture('current-catalog-mobile');
 await call('Emulation.setEmulatedMedia',{features:[{name:'forced-colors',value:'active'},{name:'prefers-reduced-motion',value:'reduce'}]});await evaluate('document.querySelector("nav a").focus()');
 check('Forced-color keyboard focus',await evaluate('matchMedia("(forced-colors:active)").matches && getComputedStyle(document.activeElement).outlineStyle==="solid"'));
 check('No off-origin assets',report.externalRequests.length===0,report.externalRequests);
 check('No browser errors',report.errors.length===0,report.errors);
 report.passed=true;
'''
    script=out/'browser.mjs';script.write_text(prefix+'try{\n'+setup+body+suffix)
    binary=pathlib.Path('/home/hoskinson/.cache/puppeteer/chrome-headless-shell/linux-154.0.8037.57/chrome-headless-shell-linux64/chrome-headless-shell')
    result=subprocess.run(['node',str(script),f'http://127.0.0.1:{server.server_port}',str(out),str(binary)],capture_output=True,text=True,timeout=90)
    (out/'browser-helper.stdout').write_text(result.stdout);(out/'browser-helper.stderr').write_text(result.stderr)
    browser=json.loads((out/'browser-report.json').read_text());report['browser']=browser
    check('Browser normal exit and checks pass',result.returncode==0 and browser['passed'] and browser['browserExitCode']==0)
    check('Documentation inputs unchanged',all(sha(root/n)==v for n,v in inputs.items()))
    report['passed']=True
except Exception as e:report['error']=repr(e)
finally:
    if server:server.shutdown();server.server_close()
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(root/'.warlock-contributor/current-docs-verification.json').write_text(json.dumps({'report':str(out/'report.json'),'passed':report['passed']})+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(out/'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])
