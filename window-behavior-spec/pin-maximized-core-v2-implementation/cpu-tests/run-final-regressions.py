import hashlib,json,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parents[1]
tests=['plugin/test_pin_action.cpp','test_pin_boundary.cpp','test_pin_stacking.cpp','test_pin_lifetime.cpp','plugin/test_modal_region.cpp','plugin/test_caption_cache.cpp','plugin/test_atlas_coordinates.cpp','cpu-tests/test_max_action.cpp']
commands=[]
for source in tests:
    name=Path(source).stem
    output=B/'cpu-tests'/('final-'+name)
    args=['g++','-std=c++26','-O1','-UNDEBUG','-I'+str(B/'plugin'),source,'-o',str(output)]
    if 'lifetime' in name:args+=['-ljson-c']
    if 'atlas' in name:args+=subprocess.check_output(['pkg-config','--cflags','--libs','hyprutils'],text=True).split()
    for phase,argv in [('compile',args),('run',[str(output)])]:
        log=B/'cpu-tests'/('final-'+name+'-'+phase+'.log')
        start=time.monotonic()
        with log.open('wb') as f:r=subprocess.run(argv,cwd=B,stdout=f,stderr=subprocess.STDOUT)
        commands.append(dict(source=source,sourceSHA256=hashlib.sha256((B/source).read_bytes()).hexdigest(),phase=phase,argv=argv,exitCode=r.returncode,elapsed=time.monotonic()-start,log=str(log.relative_to(B)),logSHA256=hashlib.sha256(log.read_bytes()).hexdigest()))
        (B/'cpu-tests/final-regression-commands.json').write_text(json.dumps(dict(nativeExecuted=False,commands=commands),indent=2)+'\n')
        print(name,phase,r.returncode,flush=True)
        if r.returncode:raise SystemExit(r.returncode)
