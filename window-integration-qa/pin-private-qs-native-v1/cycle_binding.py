"""Exact private SUPER+T binding; no input or binding at import."""
from pathlib import Path
import json,shlex,stat
from io_guard import publish_json,sha
from selection import B
from materialize import pin_config
def install(session,prepared):
 if prepared.get('published')is not True:raise ValueError('Final actual QS source registration required before binding')
 home=Path(prepared['home']);folder=home/'cycle-evidence';folder.mkdir(mode=0o700);path=home/'cycle-config.json';entry=B/'cycle_entry.py'
 # Hash cannot be embedded in the configuration containing its own command.
 # The launch command therefore carries a separate immutable hash after fsync;
 # ancestry validates that exact final command through a second small file.
 config=dict(runtime=prepared['runtime'],home=prepared['home'],evidence=str(folder),entrySHA256=sha(entry),interpreter=dict(path=str(Path('/usr/bin/python3').resolve()),sha256=sha('/usr/bin/python3')),requester=prepared['requester'],environment=prepared['environment'],command=prepared['command'],compositor=prepared['pinConfig']['compositor'])
 # Dispatcher uses exec, so the direct relay ordinarily has compositor parent.
 # An intermediate /bin/sh, when observed, is authenticated from final config.
 config['dispatchCommand']='exec /usr/bin/python3 -I -S '+shlex.quote(str(entry))+' '+shlex.quote(str(path))+' CONFIG_HASH'
 h=publish_json(path,config);command=config['dispatchCommand'].replace('CONFIG_HASH',h)
 actual=home/'cycle-dispatch.json';publish_json(actual,dict(command=command,configSHA256=h))
 raw=session.ctl('repl','hl.bind("SUPER + T", function() hl.dsp.exec('+json.dumps(command)+') end)')
 return dict(configPath=str(path),configSHA256=h,dispatch=str(actual),command=command,rawACK=raw,setupOnly=True,effectNotAcceptance=True)
