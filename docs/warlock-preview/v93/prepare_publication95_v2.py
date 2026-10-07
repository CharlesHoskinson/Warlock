"""Retry PUBLIC95 preparation without overwriting historical Native129 sources."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
original=r/'docs/warlock-preview/v93/prepare_publication95.py'
s=original.read_text()
assert s.count("p=r/'docs/warlock-preview/v93/commit129.py'")==1
s=s.replace('warlock-repository/v95/publication','warlock-repository/v95/publication-v2')
s=s.replace("p=r/'docs/warlock-preview/v93/commit129.py'", "p=r/'docs/warlock-preview/v93/commit_gui129_controlled.py'")
s=s.replace("'docs/warlock-repository/v95/publication-v2/',*(f", "'docs/warlock-repository/v95/publication/', 'docs/warlock-repository/v95/publication-v2/',*(f")
assert s.count("a=s.index('for name,passed in ')")==1
s=s.replace("a=s.index('for name,passed in ')", "s=s.replace(\"r/'docs/warlock-repository/v95/publication-v2']\", \"r/'docs/warlock-repository/v95/publication',r/'docs/warlock-repository/v95/publication-v2']\")\na=s.index('for name,passed in ')")
ast.parse(s)
exec(compile(s,str(original)+'#reviewed-v2','exec'))
