"""ELM-UI-016 ordinary picker journey using the existing protected private host.

Reuse its exact ABI checks, owned helpers, original six-second waits and normal
cleanup. Change only the FOCUS observation branch; supply no policy/source pixels.
"""
import hashlib,pathlib,sys
QUIESCENT=sys.argv[1:]==['--quiescence']
assert not sys.argv[1:] or QUIESCENT
path=pathlib.Path(__file__).with_name('native-window-feedback.py')
original=path.read_text()
start=original.index('   elif FOCUS:\n')
end=original.index('   else:\n    # Current real taskbar primary action',start)
branch=r'''   elif FOCUS:
    import re
    import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    def scheduler_rows():
     return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('picker-preview-scheduler: ')]
    def scheduler():
     rows=scheduler_rows();return rows[-1] if rows else None
    before=len(journal());click(initial)
    picker=wait(lambda:(projection() or {}).get('picker'))
    check('OrdinaryPickerOpensWithoutWindowMutation',len(journal())==before and len(picker['selections'])==2,picker=picker)
    def bodies():
     return [json.loads(line.split(' ',2)[2])['body'] for line in text().splitlines() if line.startswith('surface-report: origin=popup ')]
    def body():
     current=projection()
     return next((row for row in reversed(bodies()) if current and row['publication']==current['publication']),None)
    def live_rows():
     row=body()
     return row if row and len(row.get('previews',[]))==2 and any(p['state']=='live' and p['image'] and p['image']['complete'] and p['image']['naturalWidth']>0 for p in row['previews']) and all(p['state'] in ['live','unavailable'] for p in row['previews']) else None
    live=wait(live_rows)
    check('OrdinaryAuthorizedNativeImageLoadsWithBoundedFallback',True,body=live)
    packets=[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('picker-preview-events: ')]
    offered={event['identity']:event['event']['frame'] for batch in packets for event in batch if event['kind']=='event' and event['event']['kind']=='offer'}
    check('DifferentFamiliesHaveDifferentOpaqueFrames',len(offered)>=1 and len({frame['handle'] for frame in offered.values()})==len(offered) and all(identity=='family:'+frame['job']['context']['incarnation'] and frame['fidelity']=='family' and set(frame['coverage'])=={'client','decoration','modal','popup'} for identity,frame in offered.items()),offers=offered)
    def capture(name,observed,expected):
     matches=re.findall(r'xdg_popup[#@]\d+\.configure\((\d+), (\d+), (\d+), (\d+)\)',text());assert matches
     dx,dy,_,_=map(int,matches[-1]);image=OUTPUT/(name+'.png');helper(['/usr/bin/grim',str(image)])
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();regions=[]
     for row in observed['previews']:
      if row['identity'] not in expected or not row['image']:continue
      r=row['image'];assert r
      left,top=max(0,int(dx+r['x'])),max(0,int(dy+r['y']));right,bottom=min(pix.get_width(),int(dx+r['x']+r['width'])),min(pix.get_height(),int(dy+r['y']+r['height']))
      red=green=0
      for y in range(top,bottom):
       for x in range(left,right):
        offset=y*stride+x*channels;rr,gg,bb=pixels[offset:offset+3]
        red+=rr>180 and gg<80 and bb<80;green+=gg>180 and rr<80 and bb<80
      wanted=expected[row['identity']];regions.append({'identity':row['identity'],'region':[left,top,right,bottom],'red':red,'green':green,'expected':wanted})
      check(name+'FamilyOwnPixels'+row['identity'],(red>100 and green<50) if wanted=='red' else (green>100 and red<50),region=regions[-1])
     report.setdefault('physicalPreviewCaptures',[]).append({'path':str(image),'sha256':sha(image),'regions':regions})
    expected={'family:'+row['incarnation']:('red' if row['title']=='ELM-AUTHORITY-FIXTURE' else 'green') for row in picker['selections']}
    capture('Live',live,expected)
    loading=[row for row in bodies() if any(p['state']=='loading' and 'Preview loading' in p['text'] and p['image'] is None for p in row.get('previews',[]))]
    check('ActualLoadingDOMHasMatchingFallbackLabel',bool(loading),observations=loading)
    primary=next(row['identity'] for row in live['previews'] if row['state']=='live' and row['image'] and row['image']['complete'])
    old_handle=next(row['image']['uri'] for row in live['previews'] if row['identity']==primary)
    private_effect('minimize',primary.removeprefix('family:'))
    wait(lambda:(projection() or {}).get('mode')=='closed')
    click(wait(lambda:group('Choose a window from')))
    wait(lambda:(projection() or {}).get('picker'))
    def historical_row():
     current=body()
     return current if current and any(row['identity']==primary and row['state']=='historical' and row['image'] and row['image']['complete'] and row['image']['uri']==old_handle and 'Historical preview' in row['text'] for row in current['previews']) else None
    historical=wait(historical_row)
    check('ActualMinimizeRetainsAuthorizedHistoricalFrame',True,body=historical,uri=old_handle)
    capture('Historical',historical,{primary:expected[primary]})
    def unavailable_row():
     current=body()
     return current if current and any(row['identity']==primary and row['state']=='unavailable' and row['image'] is None and 'Preview unavailable' in row['text'] for row in current['previews']) else None
    unavailable=wait(unavailable_row)
    check('OriginalNativeExpiryShowsUnavailableWithoutBorrowing',True,body=unavailable)
    image=OUTPUT/'Unavailable.png';helper(['/usr/bin/grim',str(image)]);report.setdefault('physicalPreviewCaptures',[]).append({'path':str(image),'sha256':sha(image),'scope':'Native unavailable fallback; separate independent AT/label pixel audit remains open.'})
    check('PreviewObservationNeverDispatchesAnotherWindowEffect',len(journal())==before and len(report['nativeFixtures'])==1,frontend=journal())
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
    helper([str(keyboard)],'key 1 1\nsleep 50\nkey 1 0\nsleep 100\nsync\n')
    wait(lambda:(projection() or {}).get('mode')=='closed')
    if QUIESCENT:
     dormant=wait(lambda: scheduler() if scheduler() and scheduler()['state']=='dormant' else None)
     check('ClosedExpiredPickerRetiresRecurringSource',True,counters=dormant)
     until=time.monotonic()+1.0
     while time.monotonic()<until:s.guard();time.sleep(.025)
     quiet=scheduler()
     check('ClosedIntervalHasNoCallbackOrCatalogWork',quiet==dormant,before=dormant,after=quiet,seconds=1.0)
     before_reopen=len(journal())
     private_effect('restore',primary.removeprefix('family:'))
     click(wait(lambda:group('Choose a window from')))
     wait(lambda:(projection() or {}).get('picker'))
     def renewed_row():
      current=body()
      if not current or not any(row['state']=='live' and row['image'] and row['image']['complete'] and row['image']['naturalWidth']>0 and row['image']['uri']!=old_handle for row in current['previews']):return None
      own=next((row for row in current['previews'] if row['identity']==primary),None)
      return current if own and ((own['state']=='unavailable' and own['image'] is None and 'Preview unavailable' in own['text']) or (own['state']=='live' and own['image'] and own['image']['complete'] and own['image']['uri']!=old_handle)) else None
     renewed=wait(renewed_row)
     packets=[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('picker-preview-events: ')]
     own_jobs=[]
     for batch in packets:
      for event in batch:
       if event['kind']!='event' or event['identity']!=primary:continue
       ev=event['event'];job=None
       if ev['kind']=='offer':job=ev['frame']['job']
       elif ev['kind']=='receipt' and ev['event']['kind']=='refused':job=ev['event']['job']
       if job and job not in own_jobs:own_jobs.append(job)
     check('ReopenRevalidatesNativeIdentityAndPreservesRequestFloor',len(own_jobs)>=2 and int(own_jobs[-1]['request'])>int(offered[primary]['job']['request']) and own_jobs[-1]['context']['incarnation']==primary.removeprefix('family:') and own_jobs[-1]['context']!=offered[primary]['job']['context'],jobs=own_jobs)
     check('ReopenNeverBorrowsExpiredFrame',all(not row['image'] or row['image']['uri']!=old_handle for row in renewed['previews']),body=renewed)
     check('CurrentAcknowledgedReopenWakesScheduler',scheduler()['callbacks']>dormant['callbacks'] and scheduler()['catalogReads']>dormant['catalogReads'],before=dormant,after=scheduler())
     check('ReopenNeverReplaysWindowEffect',len(journal())==before_reopen)
     capture('Reopened',renewed,expected)
     helper([str(keyboard)],'key 1 1\nsleep 50\nkey 1 0\nsleep 100\nsync\n')
     wait(lambda:(projection() or {}).get('mode')=='closed')
     report['previewQuiescenceCounters']={'dormant':dormant,'closedInterval':quiet,'reopened':scheduler()}
    report['nativeOrdinaryPreviewsObserved']=True
    report['missingObservations']=['Two simultaneous native raster/export pairs exceed the unchanged two-allocation native budget; broader capacity/fairness remains open.','Physical loading pixels were not intercepted; native DOM label observation is weaker.','Actual assistive technology and independent original-scenario acceptance remain open.']
'''
adapted=original[:start]+branch+original[end:]
adapted=adapted.replace("'native-taskbar-focus-' if FOCUS", "('native-preview-quiescence-' if QUIESCENT else 'native-preview-states-') if FOCUS")
needle='try:\n with host.PrivateHyprSession'
assert adapted.count(needle)==1
packet={'originalPath':str(path),'originalSHA256':hashlib.sha256(original.encode()).hexdigest(),'change':'Only original FOCUS observation branch replaced with ordinary authorized picker states, optional actual idle/reopen counters and exact colored family pixel checks; original host/deadlines/isolation/cleanup retained.'}
adapted=adapted.replace(needle,"report.update(requirements=['ELM-UI-016'],scenarios=['preview-states'],scope='Actual ordinary picker native Loading DOM, Live/Historical/Unavailable and owned color/expiry journey; physical loading and actual AT/independent acceptance separate',nativePreviewRunner="+repr(packet)+")\n"+needle)
if QUIESCENT:
 adapted=adapted.replace("requirements=['ELM-UI-016'],scenarios=['preview-states']", "requirements=['ELM-UI-017'],scenarios=['quiesce','reopen']")
 adapted=adapted.replace("report['missingObservations']=['Two simultaneous", "report['missingObservations']=['Frozen numeric quiescence interval and whole-process power/wakeup/resource soak remain unqualified. Retained frames are preserved through bounded native scope/expiry cleanup; callback dormancy is established after original expiry.','Two simultaneous")
sys.argv=[str(path),'--taskbar-focus']
exec(compile(adapted,str(path),'exec'),globals())
