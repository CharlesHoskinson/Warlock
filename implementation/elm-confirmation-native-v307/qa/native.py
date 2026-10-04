import hashlib, importlib.util, json, math, os, re, shutil, socket, struct, subprocess, sys, time, traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
SOURCE=REPO/'implementation/elm-responsive-confirmation-gui-v301'
BUILD=SOURCE/'qa/build-1791150402455523192'
FIXTURE=REPO/'implementation/elm-confirmation-render-fixture-v302'
ANCESTOR=REPO/'implementation/elm-gui-bounds-native-v279'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def preflight():
    sys.path.insert(0,str(ANCESTOR/'qa'))
    ancestor=load('confirmation_ancestor',ANCESTOR/'qa/native.py')
    host,meta,_,_,_,_,inputs=ancestor.preflight()
    failure=json.loads((ROOT/'parent-failure.json').read_text())
    for path,digest in failure['files'].items():assert sha(path)==digest,path
    inputs.update(failure['files']);inputs[str(ROOT/'parent-failure.json')]=sha(ROOT/'parent-failure.json')
    def verify(path,digest):
        assert sha(path)==digest,str(path);inputs[str(path)]=digest
    review=json.loads((ANCESTOR/'qa/preflight.json').read_text());assert review['passed']
    for path,digest in review['inputs'].items():verify(path,digest)
    verify(ANCESTOR/'qa/preflight.json',sha(ANCESTOR/'qa/preflight.json'))
    report=json.loads((BUILD/'report.json').read_text());assert report['passed'] and len(report['commands'])==19 and all(c['exitCode']==0 for c in report['commands'])
    verify(BUILD/'report.json',sha(BUILD/'report.json'));verify(BUILD/'elm-host',report['binarySHA256'])
    generated={'assets/elm.js','assets/bar.js','assets/popup.js'}
    for name,digest in report['inputs'].items():
        if name in generated:continue
        verify(BUILD/'inputs'/name,digest)
        if (SOURCE/name).is_file():verify(SOURCE/name,digest)
    for name,digest in report['artifacts'].items():
        verify(BUILD/name,digest)
        if name.startswith('inputs/assets/'):verify(SOURCE/name.removeprefix('inputs/'),digest)
    for section in ('compilerDependencies','tools','linkedLibraries'):
        for path,row in report[section].items():verify(path,row['sha256'])
    probe=json.loads((REPO/'implementation/elm-picker-ready-runtime-v239/parent-probe-build.json').read_text())
    pointer=json.loads(Path(probe['buildReport']).read_text());verify(pointer['client'],pointer['clientSHA256'])
    for path in [ROOT/'SPEC.md',ROOT/'qa/native.py',ROOT/'qa/review.py',ANCESTOR/'qa/native.py',SOURCE/'SPEC.md',SOURCE/'lineage.json',FIXTURE/'SPEC.md',*sorted((FIXTURE/'qa').glob('*'))]:
        if path.is_file():verify(path,sha(path))
    return host,meta,pointer['client'],inputs

def materialize(output):
    assets=output/'fixture-assets';shutil.copytree(BUILD/'inputs/assets',assets)
    frames=json.loads((FIXTURE/'qa/frames.json').read_text())['frames']
    (assets/'adapter.js').write_text('window.fixtureFrames='+json.dumps(frames)+';\n'+(FIXTURE/'qa/driver.js').read_text())
    (assets/'index.html').write_text('<!doctype html><html><head><meta charset="utf-8"></head><body><script src="adapter.js"></script></body></html>\n')
    for name in ('bar.html','popup.html'):
        original=(BUILD/'inputs/assets'/name).read_text()
        diagnostic='<script>'+(FIXTURE/'qa/inspect.js').read_text()+'</script>'
        (assets/name).write_text(original.replace('</body>',diagnostic+'</body>'))
    return assets,frames

class Probe:
    def __init__(self,session,host,web,output,pointer,scale,check):
        self.session,self.host,self.web,self.output,self.pointer,self.scale,self.check=session,host,web,output,pointer,scale,check
        self.log=output/'confirmation.log';self.parent=next(row for _,row in session.host.processes if row['name']=='weston')
        self.socket=session.host.runtime/'weston-host';self.socket_id=host.original.socket_identity(self.socket,session.host.runtime)
        with socket.socket(socket.AF_UNIX) as s:
            s.settimeout(2);s.connect(str(self.socket));pid,uid,_=struct.unpack('3i',s.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
        check('verifiedPhysicalParent',pid==self.parent['pid'] and uid==os.getuid() and host.original.same_process(self.parent))
    def text(self):
        data=self.log.read_bytes();assert len(data)<=16*1024*1024;return data.decode(errors='replace')
    def rows(self,prefix):return [json.loads(l[len(prefix):]) for l in self.text().splitlines() if l.startswith(prefix)]
    def current(self,origin):
        rows=[r['body'] for r in self.rows('surface-report: origin='+origin+' ') if 'controls' in r.get('body',{})]
        return rows[-1] if rows else None
    def actions(self):return [r['body']['value'] for r in self.rows('surface-inspection: ') if r.get('body',{}).get('event')=='fixture-action']
    def wait(self,predicate,deadline=None):
        deadline=time.monotonic()+6 if deadline is None else deadline
        while time.monotonic()<deadline:
            self.session.guard();assert self.web.poll() is None,'GUI terminated';value=predicate()
            assert time.monotonic()<deadline,'Six-second deadline'
            if value:return value
            time.sleep(min(.025,max(0,deadline-time.monotonic())))
        raise RuntimeError('Original six-second UI deadline')
    def input(self,commands,deadline):
        self.session.guard();assert self.host.original.same_process(self.parent)
        assert self.socket_id==self.host.original.socket_identity(self.socket,self.session.host.runtime)
        remaining=deadline-time.monotonic();assert remaining>0
        result=subprocess.run([self.pointer],input='\n'.join(commands+['quit'])+'\n',text=True,capture_output=True,env=dict(self.session.host.env,ELM_PARENT_INPUT_QA='1'),cwd=self.session.host.runtime,timeout=min(3,remaining))
        rows=[json.loads(l) for l in result.stdout.splitlines()]
        self.check('physicalInputAcknowledged',result.returncode==0 and len(rows)==len(commands)+1 and rows[0].get('ready') is True and all(r.get('accepted') is True for r in rows[1:]),commands=commands,acks=rows)
        assert self.socket_id==self.host.original.socket_identity(self.socket,self.session.host.runtime) and self.host.original.same_process(self.parent)
        assert time.monotonic()<deadline
    def popup_origin(self):
        matches=re.findall(r'xdg_popup#\d+\.configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',self.text());assert matches
        return list(map(int,matches[-1]))
    def click(self,frame,control,origin,deadline):
        assert visible(control['box']['rect'],frame['viewport']),'Control clipped'
        x,y,w,h=control['box']['rect'];ox,oy=(0,0) if origin=='bar' else self.popup_origin()[:2]
        px,py=round((ox+x+w/2)*self.scale),round((oy+y+h/2)*self.scale)
        assert 0<px<800 and 0<py<600
        self.input([f'motion {px} {py}','press 272','release 272'],deadline)
    def pixels(self,frame,node,origin,name,deadline):
        rect=node['textRect'];assert visible(rect,frame['viewport'])
        ox,oy=(0,0) if origin=='bar' else self.popup_origin()[:2]
        x,y,w,h=rect;left,top=math.floor((ox+x)*self.scale),math.floor((oy+y)*self.scale)
        right,bottom=math.ceil((ox+x+w)*self.scale),math.ceil((oy+y+h)*self.scale)
        assert 0<=left<right<=800 and 0<=top<bottom<=600
        attempts=[]
        def capture():
            before=self.current(origin);assert before==frame,'Presentation changed before capture'
            path=self.output/(name+'-'+str(len(attempts))+'.png')
            result=subprocess.run(['/usr/bin/grim',str(path)],capture_output=True,env=self.session.env,timeout=min(5,max(.001,deadline-time.monotonic())))
            assert result.returncode==0,result.stderr
            raw=path.read_bytes();assert raw[:8]==bytes.fromhex('89504e470d0a1a0a') and struct.unpack('>II',raw[16:24])==(800,600)
            decoded=subprocess.run(['/usr/bin/magick',str(path),'-depth','8','rgb:-'],capture_output=True,timeout=min(5,max(.001,deadline-time.monotonic())))
            assert decoded.returncode==0 and len(decoded.stdout)==800*600*3
            count=sum(1 for yy in range(top,bottom) for xx in range(left,right) if min(decoded.stdout[(yy*800+xx)*3:(yy*800+xx)*3+3])>120)
            row={'path':str(path),'sha256':sha(path),'physicalRect':[left,top,right-left,bottom-top],'foregroundPixels':count};attempts.append(row)
            assert self.current(origin)==frame,'Presentation changed during capture'
            return row if count>=50 else None
        matched=self.wait(capture,deadline);self.check(name+':actualGlyphPixels',bool(matched),capture=matched,attempts=attempts)

def control(frame,identity):return next(c for c in frame['controls'] if c['id']==identity)
def visible(rect,viewport):
    x,y,w,h=rect;return w>0 and h>0 and x>=-.5 and y>=-.5 and x+w<=viewport[0]+.5 and y+h<=viewport[1]+.5

def run(scale):
    out=ROOT/'qa'/('native-'+str(time.time_ns()));out.mkdir()
    report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Crafted presentation only; actual301 native renderer and physical private parent input; controlled bus, no Unknown authority/AT/IME/hardware claims','scale':scale,'checks':[]}
    session=None;output=None;web=None;loaded=False
    def check(name,value,**data):
        report['checks'].append({'name':name,'passed':bool(value),**data});assert value,name
    try:
        host,meta,pointer,inputs=preflight();review=json.loads((ROOT/'qa/review.json').read_text());assert review['passed']
        for path,digest in review['inputs'].items():assert sha(path)==digest,path
        inputs.update(review['inputs']);inputs[str(ROOT/'qa/review.json')]=sha(ROOT/'qa/review.json');report['inputs']=inputs
        output=Path('/home/hoskinson/window-integration-qa')/('confirmation-'+str(time.time_ns()))
        lua=('hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=%d})\n'%scale).encode()
        with host.PrivateHyprSession(output,dict(os.environ),800,600,lua,mesa_vendor=True) as session:
            try:
                assets,frames=materialize(output);report['fixtureAssets']={str(p.relative_to(assets)):sha(p) for p in assets.iterdir() if p.is_file()}
                config=output/'fixture-control.json';configuration={'runtime':str(session.host.runtime),'instance':session.env['HYPRLAND_INSTANCE_SIGNATURE'],'name':'bar'};config.write_text(json.dumps(configuration)+'\n');config.chmod(0o600)
                check('exactCoreAndAQMapped',session.evidence['hyprlandMaps']['files'].get(str(Path(meta['binary']).resolve()))==meta['sha256'] and session.evidence['privateAquamarine']['mappedVerified'])
                check('explicitPluginLoad',session.ctl('plugin','load',meta['plugin']['path']).strip()=='ok');loaded=True
                compositor=next(row for _,row in session.host.processes if row['name']=='hyprland')
                check('exactPluginMapped',host.original.mapped_files(compositor['pid'])['files'].get(str(Path(meta['plugin']['path']).resolve()))==meta['plugin']['sha256'])
                web=session.host.launch('confirmation',[str(BUILD/'elm-host'),'--assets',str(assets),'--backend',str(FIXTURE/'qa/backend.py'),'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=dict(session.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client'))
                gui=Probe(session,host,web,output,pointer,scale,check)
                bar=gui.wait(lambda:gui.current('bar') if gui.current('bar') and len(gui.current('bar')['controls'])==3 and session.data('monitors')[0]['reserved'][1]==48 else None)
                check('actual48pxBarViewport',bar['viewport']==[800//scale,48])
                blocked=control(bar,'qa-blocked');expected=frames['bar']['bar'][1]
                check('confirmationDetailUnclippedBesideEllipsizedTitle',blocked['disabled'] and blocked['detail']['text']==expected['detail'] and visible(blocked['detail']['textRect'],bar['viewport']) and blocked['detail']['scrollWidth']<=blocked['detail']['clientWidth']+1 and blocked['label']['scrollWidth']>blocked['label']['clientWidth'])
                check('fullAccessibleLabelAndTitle',blocked['ariaLabel']==expected['ariaLabel'] and blocked['title']==expected['label']+'; '+expected['detail'])
                gui.pixels(bar,blocked['detail'],'bar','bar-confirmation',time.monotonic()+6)
                gui.click(bar,blocked,'bar',time.monotonic()+6)
                gui.input([],time.monotonic()+6)
                check('blockedBarNoAction',gui.actions()==[] and gui.current('bar')==bar)
                gui.click(bar,control(bar,'qa-open'),'bar',time.monotonic()+6)
                popup=gui.wait(lambda:gui.current('popup') if gui.current('popup') and gui.current('popup')['focus']=='qa-close' else None)
                check('actualPopupRoleAndFocus',gui.popup_origin()[2:]==popup['viewport'] and popup['lease']!='0' and gui.actions()[-1]['action']['id']=='qa-open')
                check('fullPopupStatusWrapsAndFits',popup['status']['text']==frames['popup']['status'] and visible(popup['status']['textRect'],popup['viewport']) and popup['status']['scrollWidth']<=popup['status']['clientWidth']+1)
                gui.pixels(popup,popup['status'],'popup','popup-status',time.monotonic()+6)
                before=gui.actions();gui.click(popup,control(popup,'qa-restore'),'popup',time.monotonic()+6)
                check('blockedPopupNoAction',gui.actions()==before)
                gui.input(['key-press 15','key-release 15'],time.monotonic()+6)
                focused=gui.wait(lambda:gui.current('popup') if gui.current('popup') and gui.current('popup')['focus']=='qa-popup-refresh' else None)
                check('actualTabSkipsDisabledAndReachesRefresh',visible(control(focused,'qa-popup-refresh')['box']['rect'],focused['viewport']) and all(control(focused,i)['disabled'] for i in ('qa-restore','qa-minimize','qa-maximize')))
                check('smallPopupFocusActuallyScrolls',scale!=2 or focused['scroll'][1]>0)
                gui.pixels(focused,control(focused,'qa-popup-refresh')['detail'],'popup','popup-refresh',time.monotonic()+6)
                gui.click(focused,control(focused,'qa-popup-refresh'),'popup',time.monotonic()+6)
                action=gui.wait(lambda:gui.actions()[-1] if len(gui.actions())==len(before)+1 else None)['action']
                check('popupRefreshUsesExactPresentedScope',action['id']=='qa-popup-refresh' and action['publication']==focused['publication'] and action['lease']==focused['lease'])
                gui.input(['key-press 42','key-press 15','key-release 15','key-release 42'],time.monotonic()+6)
                close=gui.wait(lambda:gui.current('popup') if gui.current('popup') and gui.current('popup')['focus']=='qa-close' else None)
                check('actualShiftTabReturnsToClose',visible(control(close,'qa-close')['box']['rect'],close['viewport']))
                gui.click(close,control(close,'qa-close'),'popup',time.monotonic()+6)
                closed=gui.wait(lambda:gui.current('bar') if gui.current('bar') and int(gui.current('bar')['publication'])>int(close['publication']) else None)
                check('actualCloseAction',gui.actions()[-1]['action']['id']=='qa-close')
                temporary=config.with_suffix('.tmp');configuration['name']='bar-focus';temporary.write_text(json.dumps(configuration)+'\n');temporary.chmod(0o600);temporary.replace(config)
                barfocused=gui.wait(lambda:gui.current('bar') if gui.current('bar') and gui.current('bar')['focus']=='qa-refresh' and int(gui.current('bar')['publication'])>int(closed['publication']) else None)
                check('nativeProgrammaticBarFocusScrollsToRefresh',visible(control(barfocused,'qa-refresh')['box']['rect'],barfocused['viewport']) and (scale!=2 or barfocused['scroll'][0]>0))
                gui.pixels(barfocused,control(barfocused,'qa-refresh')['detail'],'bar','bar-refresh',time.monotonic()+6)
                before=len(gui.actions());gui.click(barfocused,control(barfocused,'qa-refresh'),'bar',time.monotonic()+6)
                action=gui.wait(lambda:gui.actions()[-1] if len(gui.actions())==before+1 else None)['action']
                check('barRefreshUsesExactPresentedScope',action['id']=='qa-refresh' and action['publication']==barfocused['publication'] and action['lease']==barfocused['lease'])
                check('onlyFourExplicitEnabledActions',[a['action']['id'] for a in gui.actions()]==['qa-open','qa-popup-refresh','qa-close','qa-refresh'])
                check('noBackendRequestsAndNoAdmissionRefusals','frontend-request: ' not in gui.text() and 'view-refused:' not in gui.text() and 'surface-refused:' not in gui.text())
            finally:
                errors=[]
                def cleanup(name,fn):
                    try:fn()
                    except Exception as e:errors.append({'step':name,'error':repr(e)})
                def stop():
                    if web is not None:
                        owned=next(row for process,row in session.host.processes if process is web)
                        if web.poll() is None:session.host.stop(owned,web)
                        web.wait(timeout=5)
                        check('normalHostAndBackendEOF',web.returncode==0 and 'backend-exit: waited=1 normal=1 code=0' in (output/'confirmation.log').read_text())
                cleanup('stopOwnedGUI',stop)
                if loaded:
                    cleanup('emptyNativeClientCensus',lambda:check('emptyNativeClients',session.data('clients')==[]))
                    if session.data('clients')==[]:cleanup('unloadModule',lambda:check('normalPluginUnload',session.ctl('plugin','unload',meta['plugin']['path']).strip()=='ok'))
                    else:errors.append({'step':'unloadModule','error':'Refused while clients remain'})
                report['finalCleanupErrors']=errors
                if sys.exc_info()[0] is None and errors:raise RuntimeError(repr(errors))
        report['cleanup']=session.evidence
        check('normalOrderedPrivateCleanup',not any(session.evidence.get(k) for k in ('cleanupErrors','unexpectedInnerDescendants','remainingDescendants')) and session.evidence.get('runtimeGone'))
        check('noPrivateServiceActivation','Activating service name=' not in (output/'privateBus.log').read_text())
        for path,digest in report['inputs'].items():assert sha(path)==digest,path
        report['passed']=True
    except Exception as e:
        report['error']=repr(e);report['traceback']=traceback.format_exc()
    finally:
        if session is not None:report['cleanup']=session.evidence
        if output is not None and output.exists():shutil.copytree(output,out/'native-evidence')
        report['passed']=report['passed'] and not report.get('finalCleanupErrors')
        report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}),flush=True)
    return report

if __name__=='__main__':
    results=[]
    for scale in (2,1):
        result=run(scale);results.append(result)
        if not result['passed']:break
    sys.exit(0 if all(r['passed'] for r in results) else 1)
