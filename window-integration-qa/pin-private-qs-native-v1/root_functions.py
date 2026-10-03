"""Exact original read-only main observer/transport bodies, without GUI imports."""
from pathlib import Path
import ast,hashlib,json,subprocess
from types import SimpleNamespace
QA=Path('/home/hoskinson/window-integration-qa')
SOURCE=QA/'pin-maximized-native-v2/proposed/run_native.py'
def original_functions():
 tree=ast.parse(SOURCE.read_text());names={'observer','transport'}
 body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
 if {n.name for n in body}!=names:raise ValueError('Exactly original read-only functions required')
 module=ast.Module(body=body,type_ignores=[]);namespace=dict(Path=Path,subprocess=subprocess,json=json,QA=QA,re=__import__('re'))
 exec(compile(module,str(SOURCE),'exec'),namespace)
 return SimpleNamespace(**{n:namespace[n]for n in names})
