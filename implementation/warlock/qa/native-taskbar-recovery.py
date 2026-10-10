"""Current visual Pending/Refused/Unknown and read-only recovery; AT separate."""
import hashlib, pathlib, sys

assert not sys.argv[1:]
p = pathlib.Path(__file__).with_name('native-window-feedback.py')
source = p.read_text()
# Preserve the original physical actions, transport-loss stimulus, deadlines,
# receipts, native pixels, authoritative state and cleanup. Visual status is
# intentionally non-live since the scoped single-announcer integration.
needle = "o['live']=='polite'"
assert source.count(needle) == 1
source = source.replace(needle, "o['live']=='off'")
needle = "   else:\n    # Current real taskbar primary action, before adding any fault."
assert source.count(needle) == 1
source = source.replace(needle, """   else:
    report['currentRecoveryRunner']={'path':str(pathlib.Path(__file__)),'sha256':sha(pathlib.Path(__file__)),'baseRunnerSHA256':sha(p),'scope':'Current visible status aria-live off with unchanged single-announcer policy. No AT/speech acceptance; original native feedback, pixels, persistent Unknown and physical recovery checks unchanged.'}
    # Current real taskbar primary action, before adding any fault.""")
exec(compile(source, str(p), 'exec'), {'__name__': '__main__', '__file__': __file__, 'p': p})
