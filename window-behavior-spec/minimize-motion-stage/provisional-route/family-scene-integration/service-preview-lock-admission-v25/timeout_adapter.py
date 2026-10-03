"""Exact inherited Bash deadline adapter; source execution stays unchanged."""
from recovery_resources import material_path

NAME='BASH_FUNC_timeout%%'
FUNCTION='() { /usr/bin/timeout --foreground "$@"; }'
PATH='/usr/bin/timeout'

def prepare(env):
    material=material_path(PATH)
    selected=dict(env);selected[NAME]=FUNCTION
    return selected,{'name':NAME,'function':FUNCTION,'executable':PATH,'material':material}

def check(row):
    from recovery_resources import checked_material
    if not isinstance(row,dict) or set(row)!={'name','function','executable','material'} or row['name']!=NAME or row['function']!=FUNCTION or row['executable']!=PATH:raise ValueError('exact confined timeout adapter required')
    checked_material(row['material'],sealed=False)
    if row['material']!=material_path(PATH):raise ValueError('selected timeout executable changed')
