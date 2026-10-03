"""Code-path-only product launcher; preserves user XDG profile/settings."""
import os,sys
from pathlib import Path

def environment(original,base):
    env=dict(original);prefix=base/'reader-prefix'
    env.pop('DISPLAY',None);env['GDK_BACKEND']='wayland'
    # Scope module paths to this reviewed package rather than inheriting QA or
    # unrelated Python injection. Existing speech/user customization is Orca's.
    env['PYTHONPATH']=os.pathsep.join(map(str,(base,base/'orca-compat',prefix/'usr/lib/python3.14/site-packages')))
    env['LD_LIBRARY_PATH']=str(prefix/'usr/lib')
    env['GI_TYPELIB_PATH']=str(prefix/'usr/lib/girepository-1.0')
    env['XDG_DATA_DIRS']=str(prefix/'usr/share')+':'+original.get('XDG_DATA_DIRS','/usr/local/share:/usr/share')
    for name in ('ORCA_QA_UTTERANCES','ORCA_QA_LEGACY_GRAB_FIX','ORCA_QA_NATIVE_WAYLAND_MODIFIERS'):
        env.pop(name,None)
    return env

def main():
    base=Path(__file__).resolve().parent
    os.execve(sys.executable,[sys.executable,str(base/'reader_bootstrap.py'),'--manifest',str(base/'package.json'),'--',*sys.argv[1:]],environment(os.environ,base))
if __name__=='__main__':main()
