"""Exact descendant identity checks; no process control or broad allowlist."""
def identity(row):
    return (int(row['pid']),str(row['start']))
def unexpected(rows,baseline):
    accepted={identity(row) for row in baseline}
    return [row for row in rows if identity(row) not in accepted]

def portal_activations(text):
    import re
    names=re.findall(r"Activating service name='([^']+)'",text)
    return [name for name in names if name.startswith(('org.freedesktop.portal.','org.freedesktop.impl.portal.','org.gtk.vfs.'))]
