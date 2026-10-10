"""Original preview journey additionally requires two authorized live families.

Preserve original grants, pixels, five-second expiry, six-second waits and cleanup.
No holds, renderer readiness injection, substitute images or relaxed assertion.
"""
import hashlib,pathlib,sys
assert not sys.argv[1:]
base=pathlib.Path(__file__).with_name('native-preview-states.py')
source=base.read_text()
needle="    live=wait(live_rows)"
assert source.count(needle)==1
loading=r"""    def loading_now():
     current=body()
     return current if current and any(row['state']=='loading' and 'Preview loading' in row['text'] and row['image'] is None for row in current.get('previews',[])) else None
    loading_body=wait(loading_now)
    image=OUTPUT/'Loading-attempt.png';helper(['/usr/bin/grim',str(image)])
    report['loadingCaptureAttempt']={'body':loading_body,'image':str(image),'imageSHA256':sha(image),'scope':'Actual private-output screenshot after Loading DOM; physical caption/no-foreign-pixel inspection is separate and may race later paint.'}
    original_live_rows=live_rows
    def live_rows():
     current=original_live_rows()
     return current if current and all(p['state']=='live' and p['image'] and p['image']['complete'] and p['image']['naturalWidth']>0 for p in current['previews']) else None
"""
source=source.replace(needle,loading+needle)
source=source.replace(needle,needle+"\n    check('BothFamiliesHaveOwnAuthorizedLivePreviews',all(p['state']=='live' and p['image'] and p['image']['complete'] and p['image']['naturalWidth']>0 for p in live['previews']) and len(live['previews'])==2,body=live)")
source=source.replace("'native-preview-states-'","'native-picker-storage-'")
inspection=r"""    import re
    native_storage=pathlib.Path(OUTPUT/'hyprland.log').read_text(errors='replace')
    storage=[{'subject':int(subject),'items':int(items),'bytes':int(owned)} for subject,items,owned in re.findall(r'picker-sealed-storage: subject=(\d+) items=(\d+) bytes=(\d+) backingShared=1',native_storage)]
    retired=[{'subject':int(subject),'items':int(items),'bytes':int(owned)} for subject,items,owned in re.findall(r'picker-sealed-retirement: subject=(\d+) items=(\d+) bytes=(\d+)',native_storage)]
    check('ActualNativeSharedBackingsStayWithinOriginalBudget',len({row['subject'] for row in storage})>=2 and any(row['items']==2 for row in storage) and all(0<row['items']<=2 and 0<row['bytes']<=128*1024*1024 for row in storage),counters=storage)
    check('ActualNativeRetirementDrainsBothBackingSlots',any(row['items']==0 and row['bytes']==0 for row in retired),counters=retired)
    report['nativeSharedStorage']={'exports':storage,'retirements':retired,'slotLimit':2,'byteLimit':128*1024*1024}
"""
needle="    report['nativeOrdinaryPreviewsObserved']=True"
assert source.count(needle)==1
source=source.replace(needle,inspection+needle)
source=source.replace('Two simultaneous native raster/export pairs exceed the unchanged two-allocation native budget; broader capacity/fairness remains open.','Two simultaneous native family backings observed within unchanged two-allocation budget; broader capacity/fairness remains open.')
sys.argv=[str(base)]
exec(compile(source,str(base),'exec'),{'__name__':'__main__','__file__':str(base)})
