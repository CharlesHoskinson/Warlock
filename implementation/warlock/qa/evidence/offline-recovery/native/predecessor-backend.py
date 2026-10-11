import os,sys
from pathlib import Path
assert Path(sys.argv[1]).read_text()=='{"runtime": "/run/user/1000/wqa/a291", "instance": "efb50993780079460b0cbed1363e2166a2de1d9f_1791677294_688696961", "pid": 750325, "expected_start": 64539728, "binary_sha256": "bae8317a93312ffee6c83d31a38e988c01b4baad80da6e04f4fb160c54517428"}'
os.execv("/usr/bin/python3",["/usr/bin/python3","-B",'/home/hoskinson/omarchy-windows-parity/implementation/warlock/qa/runs/taskbar-primary-1791674339460650359/inputs/adapter/daemon.py','/home/hoskinson/window-integration-qa/warlock-window-feedback-1791677293128207213/search-broker-config.json'])
