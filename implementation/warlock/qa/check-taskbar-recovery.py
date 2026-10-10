"""Current compiled feedback/recovery regression; browser evidence, no native/AT claim."""
import hashlib, pathlib, sys

assert not sys.argv[1:]
p = pathlib.Path(__file__).with_name('check-feedback.py')
source = p.read_text()
needle = "manifest=json.loads((ROOT/'ANCESTRY.json').read_text());inputs={}"
assert source.count(needle) == 1
source = source.replace(needle, """current=json.loads((ROOT/'qa/current-search-build.json').read_text())
current_report=REPO/current['report'];assert sha(current_report)==current['reportSHA256']
qualified=json.loads(current_report.read_text());assert qualified['passed']
manifest={'parentSources':qualified['inputs']};inputs={} """)
needle = " (INPUT/'qa/feedback.json').write_text(json.dumps(rows))"
assert source.count(needle) == 1
source = source.replace(needle, """ report['authorityBaseline']={'path':current['report'],'sha256':current['reportSHA256']}
 report['runnerInputs']={'qa/check-feedback.py':sha(ROOT/'qa/check-feedback.py'),str(pathlib.Path(__file__).relative_to(ROOT)):sha(pathlib.Path(__file__))}
 browser_source=(INPUT/'qa/feedback-browser.mjs').read_text()
 # Visual feedback stays readable in the tree. The existing scoped single
 # announcer owns live speech; making every visual status polite duplicates it.
 assert browser_source.count("o.live==='polite'")==1
 browser_source=browser_source.replace("o.live==='polite'","o.live==='off'")
 anchor=" await capture('feedback-wide-unknown');"
 assert browser_source.count(anchor)==1
 browser_source=browser_source.replace(anchor,''' for(const state of ['Refused','Unknown','Pending']){await viewport(320,80);await show(state);check(state+' recovery is first and fits actual action viewport',await evaluate(`(()=>{const n=document.querySelector('[data-surface-control="bar:recovery-refresh"]'),r=n.getBoundingClientRect(),a=document.querySelector('.surface-actions').getBoundingClientRect();return n===document.querySelector('.surface-actions button')&&r.x>=a.x&&r.right<=a.right+1&&n.disabled===${state==='Pending'};})()`));}await viewport(1440,80);await show('Unknown');
'''+anchor)
 (INPUT/'qa/feedback-browser.mjs').write_text(browser_source)
 report['browserAdaptation']={'scope':'Same visibility, keyed-focus, recovery keyboard, stale-input and no-replay checks. Current visual status is aria-live off; scoped announcer AT acceptance separate. Recovery-first/disabled-Pending checks added at 320px.','originalSHA256':sha(ROOT/'qa/feedback-browser.mjs'),'adaptedSHA256':sha(INPUT/'qa/feedback-browser.mjs')}
""" + needle)
exec(compile(source, str(p), 'exec'), {'__name__': '__main__', '__file__': __file__, 'p': p})
