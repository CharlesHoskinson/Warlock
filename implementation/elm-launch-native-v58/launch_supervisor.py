"""Native launch argv recorder and actual fixture wait receipt."""
import json,os,subprocess,sys
from pathlib import Path
fixture,receipt,control=sys.argv[1:4];out=Path(receipt)
row={'argv':sys.argv[4:],'desktop':os.environ.get('GIO_LAUNCHED_DESKTOP_FILE'),'supervisor':os.getpid()}
child=subprocess.Popen(['/usr/bin/python3','-B',fixture,control]);row['pid']=child.pid
out.write_text(json.dumps(row)+'\n');row['returnCode']=child.wait();out.write_text(json.dumps(row)+'\n')
raise SystemExit(row['returnCode'])
