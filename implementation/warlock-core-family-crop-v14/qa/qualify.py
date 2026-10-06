import pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
for runner in ['plane.py','backdrop.py','build.py']:
 p=subprocess.run([sys.executable,'-B',str(ROOT/'qa'/runner)])
 if p.returncode:raise SystemExit(p.returncode)
