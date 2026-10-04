"""Actual static C callback exercised with real mmap/fds and xkbcommon, no display."""
import hashlib,json,pathlib,resource,shlex,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('keymap-test-'+str(time.time_ns()));(OUT/'inputs').mkdir(parents=True)
report={'passed':False,'nativeAcceptance':False,'checks':9,'inputs':{}}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
try:
 for name in ['keymap.c','keymap-test.c','private-runtime.h']:
  p=ROOT/'native'/name;(OUT/'inputs'/name).write_bytes(p.read_bytes());report['inputs'][str(p)]=sha(p)
 (OUT/'inputs/keymap-test.py').write_bytes(pathlib.Path(__file__).read_bytes())
 flags=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','wayland-client','xkbcommon'],text=True));argv=['/usr/bin/cc','-std=c11','-Wall','-Wextra','-Werror',str(OUT/'inputs/keymap-test.c'),'-o',str(OUT/'test'),*flags]
 result=subprocess.run(argv,capture_output=True,timeout=60);(OUT/'compile.stderr').write_bytes(result.stderr);assert result.returncode==0,result.stderr.decode();report['argv']=argv
 result=subprocess.run([str(OUT/'test')],cwd=OUT,capture_output=True,timeout=3);(OUT/'stdout').write_bytes(result.stdout);(OUT/'stderr').write_bytes(result.stderr);assert result.returncode==0,result.stderr.decode();assert result.stdout.endswith(b'actual-keymap-callback-checks:9\n')
 packet=json.loads(result.stdout.splitlines()[0]);assert packet['seatRegistryId']==77 and packet['format']==1 and packet['xkbShiftMask']&(packet['xkbShiftMask']-1)==0
 report.update(passed=True,binarySHA256=sha(OUT/'test'),scope='Actual production keymap callback nine fd/size/NUL/format/duplicate/file-collision controls, real xkbcommon default-map parsing only; no actual compositor or focus.')
except BaseException as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(OUT/'report.json'),'passed':report['passed'],'error':report.get('error')}));raise SystemExit(0 if report['passed'] else 1)
