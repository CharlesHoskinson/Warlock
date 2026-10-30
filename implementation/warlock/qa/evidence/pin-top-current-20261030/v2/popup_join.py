"""Read-only exact-object join for the single-output private native fixture.

Unknown, ambiguous, unacknowledged and retired lifetimes fail closed. This is
not a multi-output geometry collector or product policy implementation.
"""
import json
import re


def join(text, body, projection, target, *, native_bar_epochs):
    if not body or not projection or projection.get('phase') != 'Coherent':
        return None
    if projection.get('mode') not in ('applications', 'menu'):
        return None
    publication, lease = body.get('publication'), body.get('lease')
    if not publication or not lease or projection.get('publication') != publication:
        return None
    if body.get('mode', projection.get('mode')) != projection.get('mode'):
        return None
    if projection.get('mode') == 'menu' and (projection.get('menu') or {}).get('incarnation') != target:
        return None
    # The inherited pinned collector proves the unique current layer's actual
    # configure/ack, anchor, zero margins, size and exclusive-zone contract.
    bar = native_bar_epochs(text).get(publication)
    if not bar or tuple(bar[0]) != (800, 56) or bar[1] != lease:
        return None
    surfaces, xdgs, popups, layers = {}, {}, {}, {}
    configured, opened, committed, view_commit, topology, reported = None, None, None, None, None, None
    def live(row):
        x = xdgs.get(row['xdg'])
        parent = layers.get(row.get('parent'))
        return bool(x and x['epoch'] == row['xdgEpoch'] and x['surfaceEpoch'] is not None
                    and surfaces.get(x['surface']) == x['surfaceEpoch'] and parent
                    and parent['epoch'] == row.get('parentEpoch') and parent['surfaceEpoch'] is not None
                    and surfaces.get(parent['surface']) == parent['surfaceEpoch'])
    def unique_popup():
        rows = [(key, row) for key, row in popups.items() if live(row)]
        return rows[0] if len(rows) == 1 else None
    for index, line in enumerate(text.splitlines()):
        m = re.search(r'create_surface\(new id wl_surface[#@](\d+)\)', line)
        if m:
            surfaces[m[1]] = index
        m = re.search(r'wl_surface[#@](\d+)\.destroy\(', line)
        if m:
            surfaces.pop(m[1], None)
        m = re.search(r'get_layer_surface\(new id zwlr_layer_surface_v1[#@](\d+), wl_surface[#@](\d+), wl_output[#@](\d+), (\d+), "([^"]+)"\)', line)
        if m and m[4] == '3' and m[5] == 'elm-shell-recovery-v17':
            layers[m[1]] = dict(surface=m[2], surfaceEpoch=surfaces.get(m[2]), epoch=index, output=m[3])
        m = re.search(r'zwlr_layer_surface_v1[#@](\d+)\.(destroy|closed)\(', line)
        if m:
            layers.pop(m[1], None)
        m = re.search(r'get_xdg_surface\(new id xdg_surface[#@](\d+), wl_surface[#@](\d+)\)', line)
        if m:
            xdgs[m[1]] = dict(surface=m[2], surfaceEpoch=surfaces.get(m[2]), epoch=index)
        m = re.search(r'xdg_surface[#@](\d+)\.get_popup\(new id xdg_popup[#@](\d+), nil, xdg_positioner[#@]\d+\)', line)
        if m and m[1] in xdgs:
            popups[m[2]] = dict(xdg=m[1], xdgEpoch=xdgs[m[1]]['epoch'], epoch=index)
        m = re.search(r'zwlr_layer_surface_v1[#@](\d+)\.get_popup\(xdg_popup[#@](\d+)\)', line)
        if m and m[2] in popups:
            popups[m[2]]['parent'] = m[1]
            popups[m[2]]['parentEpoch'] = layers.get(m[1], {}).get('epoch')
        m = re.search(r'xdg_popup[#@](\d+)\.configure\((-?\d+), (-?\d+), (\d+), (\d+)\)', line)
        if m and m[1] in popups:
            row = popups[m[1]]
            row.update(rect=tuple(map(int, m.groups()[1:])), configureLine=index)
            x = xdgs.get(row['xdg'])
            if x:
                x.pop('ack', None)
        m = re.search(r'xdg_surface[#@](\d+)\.(configure|ack_configure)\((\d+)\)', line)
        if m and m[1] in xdgs:
            row = xdgs[m[1]]
            if m[2] == 'configure':
                row.update(serial=m[3], serialLine=index, ack=None)
            else:
                row['ack'] = m[3] if row.get('serial') == m[3] else None
        m = re.search(r'(xdg_popup|xdg_surface)[#@](\d+)\.(destroy|popup_done)\(', line)
        if m:
            (popups if m[1] == 'xdg_popup' else xdgs).pop(m[2], None)
        m = re.fullmatch(r'surface-configured: lease=(\d+) rectKnown=[01] gdkWidth=(\d+) gdkHeight=(\d+)', line)
        if m:
            current = unique_popup()
            configured = (m[1], current[0], current[1]['epoch'], tuple(map(int, m.groups()[1:])), current[1].get('configureLine')) if current and current[1].get('rect', (0, 0, 0, 0))[2:] == tuple(map(int, m.groups()[1:])) else None
        m = re.fullmatch(r'surface-popup-open: lease=(\d+)', line)
        if m:
            current = unique_popup()
            x = xdgs.get(current[1]['xdg'], {}) if current else {}
            opened = configured if configured and current and configured[:3] == (m[1], current[0], current[1]['epoch']) and x.get('ack') and x.get('ack') == x.get('serial') and x.get('serialLine', -1) > current[1].get('configureLine', -1) else None
        m = re.fullmatch(r'surface-popup-closed: lease=(\d+)', line)
        if m and opened and m[1] == opened[0]:
            opened = None
        m = re.fullmatch(r'surface-commit: publication=(\d+) lease=(\d+) open=([01])', line)
        if m:
            committed = m.groups()
        m = re.fullmatch(r'view-commit: popup=(\d+) focus=(\d+) publication=(\d+)', line)
        if m:
            view_commit = m.groups()
        if line.startswith('view-topology: '):
            topology = json.loads(line.split(': ', 1)[1])
        if line.startswith('surface-report: origin=popup '):
            reported = json.loads(line.split(' ', 2)[2])['body']
    current = unique_popup()
    if not current or not opened or opened[:3] != (lease, current[0], current[1]['epoch']):
        return None
    key, row = current
    if not configured or configured[:3] != (lease, key, row['epoch']) or configured[4] != row.get('configureLine'):
        return None
    parent = layers.get(row.get('parent'))
    x = xdgs.get(row['xdg'], {})
    if len(layers) != 1 or not parent or parent['epoch'] != row.get('parentEpoch') or not x.get('ack') or x.get('ack') != x.get('serial') or x.get('serialLine', -1) <= row.get('configureLine', -1):
        return None
    if committed != (publication, lease, '1') or not view_commit or view_commit[2] != publication or view_commit[0] == '0' or reported != body:
        return None
    owner = view_commit[0]
    if not topology or len(topology.get('views', [])) != 1 or topology['views'][0]['id'] != owner:
        return None
    locations = topology.get('locations', [])
    if len(locations) != 1 or locations[0].get('scope') != topology['views'][0] or locations[0].get('box') != [0, 0, 800, 600]:
        return None
    rect = row.get('rect')
    if not rect or rect[2:] != (body.get('viewportWidth'), body.get('viewportHeight')) or rect[2:] != configured[3]:
        return None
    return dict(rect=list(rect), popup=key, popupEpoch=row['epoch'], xdg=row['xdg'], xdgEpoch=row['xdgEpoch'],
                surface=x['surface'], surfaceEpoch=x['surfaceEpoch'], parent=row['parent'], parentEpoch=parent['epoch'],
                serial=x['serial'], owner=owner, generation=topology['views'][0]['generation'], publication=publication, lease=lease)
