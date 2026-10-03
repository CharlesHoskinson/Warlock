#!/usr/bin/env python3
"""Test-only idle daemon. Factory/provider refuse all native/window requests."""
import argparse
import json
import os
from service_runtime import RuntimeService

def forbidden(*args):raise RuntimeError('idle lifecycle fixture cannot construct actors or observe windows')

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args()
    service=None
    try:
        service=RuntimeService(a.root,'private-session',forbidden,forbidden)
        service.start();print(json.dumps({'ready':True,'pid':os.getpid(),'actors':service.manager.state()}),flush=True)
        while not service.stop_requested.wait(.1):service.manager.watchdog()
        service.close();return 0
    except Exception as error:
        print(json.dumps({'ready':False,'error':str(error)}),flush=True)
        if service:
            try:service.close()
            except Exception:pass
        return 2

if __name__=='__main__':raise SystemExit(main())
