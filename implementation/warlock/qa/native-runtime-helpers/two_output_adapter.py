"""Build an additive two-output host adapter around an already reviewed host.

The caller supplies verify_build, which revalidates independently pinned build
and provider hashes on each use; the base host retains scope and EOF checks.
"""
from pathlib import Path


def wrap(existing, verify_build):
    class ReviewedWestonHost(existing.ReviewedWestonHost):
        def verify(self):
            super().verify(); report=verify_build()
            self.evidence['twoOutputShell']={'path':report['module']['path'], 'sha256':report['module']['sha256'], 'placement':'WAYLAND-1=headless; WAYLAND-2=warlock-qa-headless-2'}

        def launch(self,name,command,env=None):
            if name=='weston':
                report=verify_build(); old=str(existing.original.PREFIX/'usr/lib/weston/kiosk-shell.so')
                replacement='kiosk-shell.so='+old; mapping=self.env.get('WESTON_MODULE_MAP','')
                required=('--backend=headless','--renderer=gl','--shell=kiosk-shell.so','--width=800','--height=600','--scale=1','--fake-seat','--no-config')
                if mapping.split(';').count(replacement)!=1 or not all(x in command for x in required):
                    raise RuntimeError('Two-output parent differs from reviewed fixture')
                self.env['WESTON_MODULE_MAP']=';'.join(('kiosk-shell.so='+report['module']['path']) if x==replacement else x for x in mapping.split(';'))
                self.evidence['privateEnv']['WESTON_MODULE_MAP']=self.env['WESTON_MODULE_MAP']
                if env is not None: env=dict(env); env['WESTON_MODULE_MAP']=self.env['WESTON_MODULE_MAP']
            return super().launch(name,command,env)

        def __enter__(self):
            super().__enter__()
            try:
                report=verify_build(); mapped=self.evidence['westonMaps']['files']
                new=str(Path(report['module']['path']).resolve()); old=str((existing.original.PREFIX/'usr/lib/weston/kiosk-shell.so').resolve())
                probe=existing.original.verify_fresh(); input_module=str(Path(probe['module']).resolve())
                if mapped.get(new)!=report['module']['sha256'] or old in mapped or mapped.get(input_module)!=probe['moduleSHA256']:
                    raise RuntimeError('Parent mapped shell/input module mismatch')
                self.evidence['twoOutputShell']['mappedVerified']=True
                return self
            except BaseException:
                self.close(); raise

    class PrivateHyprSession(existing.PrivateHyprSession):
        def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
            dri_prime=dri_prime or 'pci-0000_00_02_0'
            super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
            self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor); self.evidence=self.host.evidence
    return ReviewedWestonHost, PrivateHyprSession
