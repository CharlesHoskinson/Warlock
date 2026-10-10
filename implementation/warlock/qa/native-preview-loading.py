"""Observe a real Loading screenshot within the unchanged preview journey.

No transport holds, synthetic readiness, capture extensions or oracle removal.
The screenshot alone is retained for inspection, not asserted as Loading paint.
"""
import hashlib,pathlib,sys
assert not sys.argv[1:]
base=pathlib.Path(__file__).with_name('native-preview-states.py')
source=base.read_text()
needle="    live=wait(live_rows)"
assert source.count(needle)==1
inspection=r'''    def loading_now():
     current=body()
     return current if current and any(row['state']=='loading' and 'Preview loading' in row['text'] and row['image'] is None for row in current.get('previews',[])) else None
    loading_body=wait(loading_now)
    image=OUTPUT/'Loading-attempt.png';helper(['/usr/bin/grim',str(image)])
    report['loadingCaptureAttempt']={'body':loading_body,'image':str(image),'imageSHA256':sha(image),'scope':'Actual private-output screenshot taken after Loading DOM observation; may race later capture completion. Physical Loading label and absence of foreign pixels require image inspection, not this DOM check.'}
'''
source=source.replace(needle,inspection+needle)
source=source.replace("'native-preview-states-'", "'native-preview-loading-'")
sys.argv=[str(base)]
exec(compile(source,str(base),'exec'),{'__name__':'__main__','__file__':str(base),'loadingWrapperSHA256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()})
