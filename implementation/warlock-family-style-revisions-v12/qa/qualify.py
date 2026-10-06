import pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
for name in ['test.py','model.py']:
 p=subprocess.run([sys.executable,'-B',str(ROOT/'qa'/name)])
 if p.returncode:raise SystemExit(p.returncode)
