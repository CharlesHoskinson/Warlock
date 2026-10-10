"""Original ordinary preview expiry with owned application artwork and AT.

Compose the existing picker journey; preserve its native grants, five-second
expiry, six-second waits, real colored families, helper limits and cleanup.
"""
import pathlib,sys
fallback_only=sys.argv[1:]==['--fallback-only']
assert not sys.argv[1:] or fallback_only
base=pathlib.Path(__file__).with_name('native-preview-states.py')
source=base.read_text()
needle='start=original.index'
assert source.count(needle)==1
arrangement=r"""
original=original.replace("ACCESSIBILITY=sys.argv[1:]==['--accessibility']","ACCESSIBILITY=True").replace("SWITCHER=sys.argv[1:]==['--switcher'] or ACCESSIBILITY","SWITCHER=sys.argv[1:]==['--switcher']")
needle="   if MOTION:\n    gtk_root="
assert original.count(needle)==1
setup=r'''   import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
   own_icon=s.host.runtime/'own-application-icon.png';pixels=GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,True,8,48,48);pixels.fill(0x00ffffff);pixels.savev(str(own_icon),'png',[],[])
   own_apps=pathlib.Path(env['XDG_DATA_HOME'])/'applications';own_apps.mkdir(parents=True,mode=0o700,exist_ok=True)
   own_desktop=own_apps/'org.warlock.PreviewFallback.desktop';own_desktop.write_text('[Desktop Entry]\nType=Application\nName=Warlock preview fixture\nStartupWMClass=WarlockPreviewFallbackFixture\nIcon='+str(own_icon)+'\nExec=/usr/bin/true\n')
   original_fixture=FIXTURE;owned_fixture=OUTPUT/'preview-fallback-fixture.py';fixture_text=FIXTURE.read_text();fixture_needle='from gi.repository import Gdk, GLib, Gtk';assert fixture_text.count(fixture_needle)==1;owned_fixture.write_text(fixture_text.replace(fixture_needle,fixture_needle+"\nGLib.set_prgname('WarlockPreviewFallbackFixture')"));FIXTURE=owned_fixture
   report['applicationIconFixture']={'desktop':str(own_desktop),'desktopSHA256':sha(own_desktop),'icon':str(own_icon),'iconSHA256':sha(own_icon),'class':'WarlockPreviewFallbackFixture','exactDesktopFilenameAbsent':not (own_apps/'WarlockPreviewFallbackFixture.desktop').exists(),'fixture':str(owned_fixture),'fixtureSHA256':sha(owned_fixture),'originalFixtureSHA256':sha(original_fixture),'scope':'Owned GTK program class differs from desktop filename; actual StartupWMClass association, cyan PNG artwork and original red/green native window content.'}
'''
original=original.replace(needle,setup+needle)
"""
source=source.replace(needle,arrangement+'\n'+needle)
needle="    check('PreviewObservationNeverDispatchesAnotherWindowEffect'"
assert source.count(needle)==1
inspection=r'''    titles={'family:'+row['incarnation']:row['title'] for row in picker['selections']}
    def fallback_rows():
     current=body()
     return current if current and len(current['previews'])==2 and all(row['state']=='unavailable' and row['image'] is None and row.get('title',{}).get('text')==titles[row['identity']] and row.get('icon') and row['icon']['complete'] and row['icon']['naturalWidth']==48 and row['icon']['naturalHeight']==48 for row in current['previews']) else None
    fallback=wait(fallback_rows)
    check('ExpiredPreviewHasExactIncarnationTitleAndApplicationIcon',all(row['icon']['uri'].startswith('elm-shell://icon/') for row in fallback['previews']) and len({row['icon']['uri'] for row in fallback['previews']})==2,body=fallback)
    metadata=[event for line in text().splitlines() if line.startswith('picker-preview-events: ') for event in json.loads(line.split(': ',1)[1]) if event.get('kind')=='metadata']
    check('NativeMetadataSelectsDeclaredApplicationArtwork',all(any(event['identity']==row['identity'] and event['application']=='WarlockPreviewFallbackFixture' and event['iconKind']=='application' and 'elm-shell://icon/'+event['icon']==row['icon']['uri'] for event in metadata) for row in fallback['previews']),metadata=metadata)
    image=OUTPUT/'ApplicationFallback.png';helper(['/usr/bin/grim',str(image)])
    matches=re.findall(r'xdg_popup[#@]\d+\.configure\((\d+), (\d+), (\d+), (\d+)\)',text());dx,dy,_,_=map(int,matches[-1]);pix=GdkPixbuf.Pixbuf.new_from_file(str(image));raw=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();regions=[]
    for row in fallback['previews']:
     def region(rect):
      left=max(0,int(dx+rect['x']));top=max(100,int(dy+rect['y']));right=min(pix.get_width(),int(dx+rect['x']+rect['width']));bottom=min(pix.get_height(),int(dy+rect['y']+rect['height']));cyan=red=green=bright=0
      for y in range(top,bottom):
       for x in range(left,right):
        offset=y*stride+x*channels;rr,gg,bb=raw[offset:offset+3];cyan+=rr<80 and gg>180 and bb>180;red+=rr>180 and gg<80 and bb<80;green+=gg>180 and rr<80 and bb<80;bright+=rr>180 and gg>180 and bb>180
      return {'bounds':[left,top,right,bottom],'area':(right-left)*(bottom-top),'cyan':cyan,'red':red,'green':green,'bright':bright}
     icon=region(row['icon']);title=region(row['title']);regions.append({'identity':row['identity'],'icon':icon,'title':title})
     check('CurrentApplicationIconActuallyPaints'+row['identity'],icon['area']>100 and icon['cyan']>.9*icon['area'] and icon['red']==0 and icon['green']==0,region=icon)
     check('CurrentWindowTitleActuallyPaints'+row['identity'],title['bright']>20,region=title,text=row['title']['text'])
    report['applicationFallback']={'body':fallback,'metadata':metadata,'image':str(image),'imageSHA256':sha(image),'regions':regions}
    names={button['accessibleName'] for button in fallback['buttons'] if button['identity'] in titles}
    def at_fallback():
     current=at_observe();nodes=[node for node in current['nodes'] if node.get('pid')==web.pid and node['name'] in names and node['role'] in ['push button','button','toggle button'] and not any(a['role']=='tool bar' and a['name']=='Warlock taskbar' for a in node['ancestors'])]
     return (current,nodes) if len(nodes)==2 and all({'enabled','sensitive','visible','showing'}<=set(n['states']) for n in nodes) else None
    at,nodes=wait(at_fallback);check('ActualAtNamesRemainExactAfterPreviewExpiry',all(any(title in node['name'] for title in titles.values()) for node in nodes),nodes=nodes);report['applicationFallback']['at']=at
'''
source=source.replace(needle,inspection+needle)
# The current shared runner documents parent output sizing before its session.
# Match that unchanged boundary rather than requiring the old adjacent lines.
source=source.replace("needle='try:\\n with host.PrivateHyprSession'", "needle='try:\\n # Each nested Wayland output'")
source=source.replace("report['missingObservations']=['Two simultaneous", "report['missingObservations']=['Independent original-scenario acceptance, native AT passive description and physical Loading pixels remain separate.','Two simultaneous")
source=source.replace("requirements=['ELM-UI-016'],scenarios=['preview-states']","requirements=['ELM-UX-007','ELM-UI-016'],scenarios=['ux-007','preview-states']")
if fallback_only:
    # UX-007's original oracle is the expired fallback, not UI-016's Loading
    # observation. Default mode keeps every UI-016 assertion. Preserve full
    # campaign failures and report this separate scenario's exact scope.
    source=source.replace("check('ActualLoadingDOMHasMatchingFallbackLabel',bool(loading),observations=loading)","report['loadingDOMObservedOutsideSelectedScenario']=bool(loading)")
    source=source.replace("requirements=['ELM-UX-007','ELM-UI-016'],scenarios=['ux-007','preview-states']","requirements=['ELM-UX-007'],scenarios=['ux-007']")
    source=source.replace("scope='Actual ordinary picker native Loading DOM, Live/Historical/Unavailable and owned color/expiry journey; physical loading and actual AT/independent acceptance separate'","scope='Original UX-007 expired retained preview: current application icon/title, actual native pixels and AT names; UI-016 Loading and independent acceptance remain separate'")
sys.argv=[str(base)]
exec(compile(source,str(base),'exec'),{'__name__':'__main__','__file__':str(base)})
