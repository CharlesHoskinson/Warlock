#!/usr/bin/env python3
"""Compile the single shared token source and copy its published exports."""
import json, pathlib, runpy, shutil
p = pathlib.Path(__file__).resolve().parent
shared = p.parents[1] / 'assets' / 'shared'
runpy.run_path(str(shared / 'authoring' / 'compile.py'), run_name='__main__')
for name in ('tokens.json', 'tokens.css', 'contrast.json'):
    shutil.copyfile(shared / name, p / name)
data = json.loads((shared / 'tokens.json').read_text())
def resolve(v):
    seen = set()
    while isinstance(v, str) and v.startswith('{') and v.endswith('}'):
        path = v[1:-1]
        if path in seen: raise ValueError('Alias cycle: ' + path)
        seen.add(path)
        node = data
        for part in path.split('.'): node = node[part]
        v = node['$value']
    return v
out = {}
for theme in ('night', 'dawn', 'high-contrast'):
    c = data['sys'][theme]['color']
    color = lambda role: resolve(c[role]['$value'])['hex'].lower().lstrip('#')
    out[theme] = {'general.border_size': 2, 'general.col.active_border': 'rgba('+color('window-edge-focused')+'ff)', 'general.col.inactive_border': 'rgba('+color('window-edge-unfocused')+'ff)', 'decoration.dim_inactive': False, 'decoration.dim_strength': 0, 'decoration.active_opacity': 1, 'decoration.inactive_opacity': 1, 'decoration.fullscreen_opacity': 1}
(p / 'hyprland.json').write_text(json.dumps(out, indent=2)+'\n')
