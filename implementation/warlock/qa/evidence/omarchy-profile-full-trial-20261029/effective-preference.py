"""Read-only private Omarchy observations; caller owns processes and input."""
import hashlib, json, os, pathlib, stat

PINS = {
 '/usr/bin/quickshell':'6c56d84cef7ac7d992de1628020f21ef722f957efb2233f2e66e1f2bb135e97c',
 '/usr/share/omarchy/shell/shell.qml':'1c390bb1703a8372a7d3a614bc44513b6cc91eee21f4bd507198e8601310e617',
 '/usr/share/omarchy/shell/plugins/bar/Bar.qml':'a8f27b3d8f29f8b8c14a5e578ad0617e6035375ccab0178a28c435e80a2822f0',
 '/usr/share/omarchy/shell/plugins/panels/clock/BarWidget.qml':'cfcdaeedc4ae5832b37271a84bb92ee762301022e2443a0f769992fa792acf28',
 '/usr/share/omarchy/shell/plugins/menu/BarWidget.qml':'ad201156483711ba77ec97303183bc02922248e97ac0c0b8ea30d250e57cd0af',
 '/usr/share/omarchy/shell/plugins/menu/Menu.qml':'f9281b8dff630c9f3f404800786052a12ccca5bab5db9095fc76eae9cd7b4fd9',
 '/usr/bin/env':'a9ba02dcad338ee7f0b03e58a1cf44009b2bd645b09c2b423242e9791d202301',
 '/usr/bin/bash':'c14c8f498f3be96f076ceb07d65dba584a86dca3c86b5dce65ed0f6cae73358d',
 '/usr/bin/timeout':'629cb6e82df4bb47188eec340f2ceb5f45def2e7b1aac1bd7443beecdcb42a6a',
 '/usr/bin/omarchy-shell':'538ece231aba80154c76ab48df8ab013b2f02c5171241d08bddbf08a5fe5ac34'}

def digest(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def clock(config):
    layout=config['bar']['layout']; rows=[x for part in layout.values() for x in part if isinstance(x,dict) and x.get('id')=='omarchy.clock']
    if len(rows)!=1 or not isinstance(rows[0].get('format'),str) or not rows[0]['format']: raise RuntimeError('clock format unavailable or ambiguous')
    return rows[0]['format']

def observe_predecessor(session, env, pid, start, config_sha256, run_ipc):
    """run_ipc(argv, env, timeout=5) -> {returncode:int, stdout:str}; caller owns it."""
    runtime=pathlib.Path(env['XDG_RUNTIME_DIR']); home=pathlib.Path(env['HOME'])
    config=home/'.config/omarchy/shell.json'; socket=runtime/env['WAYLAND_DISPLAY']
    if not runtime.is_absolute() or runtime.resolve()!=runtime or not home.is_relative_to(runtime) or home.resolve()!=home or socket.parent!=runtime: raise RuntimeError('foreign private identity')
    if env.get('OMARCHY_PATH')!='/usr/share/omarchy' or not env.get('HYPRLAND_INSTANCE_SIGNATURE') or not env.get('DBUS_SESSION_BUS_ADDRESS'): raise RuntimeError('private routing missing')
    if pathlib.Path('/usr/bin/qs').resolve()!=pathlib.Path('/usr/bin/quickshell') or pathlib.Path('/usr/share/omarchy/bin/omarchy-shell').resolve()!=pathlib.Path('/usr/bin/omarchy-shell') or pathlib.Path('/bin/bash').resolve()!=pathlib.Path('/usr/bin/bash'): raise RuntimeError('helper alias changed')
    for path,expected in PINS.items():
        if digest(path)!=expected: raise RuntimeError('installed input changed: '+path)
    if config.is_symlink() or config.resolve()!=config or digest(config)!=config_sha256: raise RuntimeError('private configuration changed')
    st=socket.lstat()
    if not stat.S_ISSOCK(st.st_mode) or st.st_uid!=os.getuid(): raise RuntimeError('private Wayland socket invalid')
    identity=(st.st_dev,st.st_ino,st.st_uid)
    def guard():
        session.guard(); p=pathlib.Path('/proc')/str(pid)
        fields=(p/'stat').read_text().rpartition(') ')[2].split()
        if fields[0]=='Z' or fields[19]!=str(start) or (p/'exe').resolve()!=pathlib.Path('/usr/bin/quickshell'): raise RuntimeError('predecessor identity changed')
        actual=dict(item.split(b'=',1) for item in (p/'environ').read_bytes().split(b'\0') if b'=' in item)
        for name in ('HOME','XDG_RUNTIME_DIR','WAYLAND_DISPLAY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS'):
            if actual.get(name.encode())!=env[name].encode(): raise RuntimeError('predecessor routing differs: '+name)
        current=socket.lstat()
        if (current.st_dev,current.st_ino,current.st_uid)!=identity or digest(config)!=config_sha256: raise RuntimeError('socket or configuration changed')
    def call(method):
        guard(); argv=['/usr/bin/quickshell','ipc','-p','/usr/share/omarchy/shell','call','shell',method]
        result=run_ipc(argv,env,5)
        if result['returncode']!=0: raise RuntimeError('IPC failed: '+method)
        values=[]
        for line in result['stdout'].splitlines():
            try:
                value=json.loads(line)
                if isinstance(value,str): value=json.loads(value)
                if isinstance(value,(dict,list)): values.append(value)
            except (ValueError,TypeError): pass
        if len(values)!=1: raise RuntimeError('ambiguous IPC result: '+method)
        guard(); return values[0]
    guard(); private=json.loads(config.read_text()); effective=call('listShellConfig'); geometry=call('debugBarGeometry')
    if not isinstance(effective,dict) or not isinstance(geometry,list) or clock(effective)!=clock(private): raise RuntimeError('effective clock differs from private config')
    layers=session.data('layers'); bars=[r for output in layers.values() for level in output.get('levels',{}).values() for r in level if r.get('namespace')=='omarchy-bar' and r.get('pid')==pid and r.get('w',0)>0 and r.get('h',0)>0 and r.get('alpha',0)>0]
    if len(bars)!=1: raise RuntimeError('owned bar ambiguous')
    def widget(name):
        found=[v for v in geometry if isinstance(v,dict) and v.get('id')==name and v.get('visible') is True and v.get('itemVisible') is True and all(type(v.get(k)) in (int,float) and v[k]>0 for k in ('width','height','itemWidth','itemHeight'))]
        if len(found)!=1: raise RuntimeError('widget unavailable: '+name)
        return found[0]
    menu=widget('omarchy.menu'); clock_widget=widget('omarchy.clock'); bar=bars[0]
    for item in (menu,clock_widget):
        if any(type(item.get(k)) not in (int,float) for k in ('x','y')) or item['x']<0 or item['y']<0 or item['x']+item['width']>bar['w'] or item['y']+item['height']>bar['h']: raise RuntimeError('widget outside owned bar')
    guard();return {'pid':pid,'start':str(start),'home':str(home),'configSHA256':config_sha256,'socketIdentity':list(identity),'clockFormat':clock(effective),'bar':bar,'clock':clock_widget,'menu':menu,'effectiveConfig':effective}

def activate_menu(observe, dispatch, wait_menu):
    """Caller supplies fresh observe(), physical dispatch(x,y), and bounded wait_menu(pid)."""
    current=observe(); bar=current['bar']; menu=current['menu']
    x=round(bar.get('x',0)+menu['x']+menu['width']/2); y=round(bar.get('y',0)+menu['y']+menu['height']/2)
    if not (0<=x<800 and 0<=y<600): raise RuntimeError('menu target outside private output')
    dispatch(x,y)
    evidence=wait_menu(current['pid'])
    if not isinstance(evidence,dict) or evidence.get('namespace')!='omarchy-menu' or evidence.get('pid')!=current['pid'] or evidence.get('w',0)<=0 or evidence.get('h',0)<=0 or evidence.get('alpha',0)<=0: raise RuntimeError('owned menu not observed')
    after=observe()
    if (after['pid'],after['start'],after['socketIdentity'],after['configSHA256'])!=(current['pid'],current['start'],current['socketIdentity'],current['configSHA256']): raise RuntimeError('predecessor changed after menu action')
    return {'point':[x,y],'menuLayer':evidence,'before':current,'after':after}
