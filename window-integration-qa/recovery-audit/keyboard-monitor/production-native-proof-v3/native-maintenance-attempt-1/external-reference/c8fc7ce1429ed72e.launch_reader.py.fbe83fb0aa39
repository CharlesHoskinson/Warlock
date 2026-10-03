"""Code-path-only product launcher; preserves user XDG profile/settings."""
import argparse,os,sys
from pathlib import Path

def environment(original,base):
    env=dict(original);prefix=base/'reader-prefix'
    env.pop('DISPLAY',None);env['GDK_BACKEND']='wayland';env['PYTHONDONTWRITEBYTECODE']='1'
    # Scope module paths to this reviewed package rather than inheriting QA or
    # unrelated Python injection. Existing speech/user customization is Orca's.
    env['PYTHONPATH']=os.pathsep.join(map(str,(base,base/'orca-compat',prefix/'usr/lib/python3.14/site-packages')))
    env['LD_LIBRARY_PATH']=str(prefix/'usr/lib')
    env['GI_TYPELIB_PATH']=str(prefix/'usr/lib/girepository-1.0')
    env['XDG_DATA_DIRS']=str(prefix/'usr/share')+':'+original.get('XDG_DATA_DIRS','/usr/local/share:/usr/share')
    for name in ('ORCA_QA_UTTERANCES','ORCA_QA_LEGACY_GRAB_FIX','ORCA_QA_NATIVE_WAYLAND_MODIFIERS'):
        env.pop(name,None)
    return env

def bootstrap_arguments(arguments,base):
    parser=argparse.ArgumentParser(add_help=False,allow_abbrev=False)
    parser.add_argument('--instance')
    # Restrict target syntax to a single explicit option before the separator;
    # preserve every remaining Orca argument byte-for-byte.
    head=arguments[:arguments.index('--')] if '--' in arguments else list(arguments)
    tail=arguments[arguments.index('--')+1:] if '--' in arguments else []
    if sum(value=='--instance' or value.startswith('--instance=') for value in head)>1:parser.error('duplicate --instance')
    target,remaining=parser.parse_known_args(head)
    result=['--manifest',str(base/'package.json')]
    if target.instance is not None:result+=['--instance',target.instance]
    return [*result,'--',*remaining,*tail]

def main():
    base=Path(__file__).resolve().parent
    os.execve(sys.executable,[sys.executable,str(base/'reader_bootstrap.py'),*bootstrap_arguments(sys.argv[1:],base)],environment(os.environ,base))
if __name__=='__main__':main()
