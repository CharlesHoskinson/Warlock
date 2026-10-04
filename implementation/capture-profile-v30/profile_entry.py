"""Explicit entry runner; must be invoked through protected qa_run.py."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
import phase_trace
ROOT=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--entry',required=True);p.add_argument('args',nargs=argparse.REMAINDER);args=p.parse_args()
 manifest=json.loads((ROOT/'source-manifest.json').read_text());source=Path(manifest['original_root'])
 for row in manifest['files']:
  for location,field in ((source,'original_sha256'),(ROOT,'derivative_sha256')):
   if hashlib.sha256((location/row['name']).read_bytes()).hexdigest()!=row[field]:raise ValueError('profile source changed')
 entry=Path(args.entry).resolve()
 if entry.parent!=source or entry.suffix!='.py':raise ValueError('entry must be an original reviewed V29 source entry')
 sys.path.insert(0,str(source));sys.path.insert(0,str(ROOT));sys.argv=[str(entry),*args.args]
 phase_trace.active=phase_trace.Trace()
 try:runpy.run_path(str(entry),run_name='__main__')
 finally:
  try:phase_trace.active.publish(args.trace)
  finally:phase_trace.active=None
if __name__=='__main__':main()
