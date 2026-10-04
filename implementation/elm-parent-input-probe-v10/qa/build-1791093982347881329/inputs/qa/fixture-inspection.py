"""Join actual GTK receipts with the one independently observed child window.

No injection return value is an event receipt. Parent points require actual
parent destination dimensions and unrotated child monitor facts from the runner.
"""
import json
import math
from pathlib import Path

TITLE = 'ELM-PARENT-INPUT-PROBE'
RECIPIENT = 'parent-input-recipient'


def receipts(path):
    records = []
    raw = Path(path).read_bytes() if Path(path).exists() else b''
    # An incomplete final write is observed on the next polling iteration.
    for line in raw.splitlines(keepends=True):
        if not line.endswith(b'\n'):
            break
        record = json.loads(line)
        if record.get('schema') != 1 or record.get('title') != TITLE or record.get('eventRecipient') != RECIPIENT:
            raise ValueError('Unexpected fixture receipt identity')
        if type(record.get('sequence')) is not int or record['sequence'] != len(records) + 1:
            raise ValueError('Non-contiguous fixture receipts')
        records.append(record)
    return records


def inspect(path, clients):
    records = receipts(path)
    if not records:
        return None
    pid = records[0]['pid']
    if any(record['pid'] != pid or record['fixtureWindowId'] != 'ordinary-1' for record in records):
        raise ValueError('Fixture window identity changed')
    candidates = [client for client in clients if client.get('pid') == pid and client.get('title') == TITLE]
    if not candidates:
        return None
    if len(candidates) != 1:
        raise ValueError('Fixture native window identity is ambiguous')
    client = candidates[0]
    latest = records[-1]
    geometry = latest['geometry']
    if not geometry['mapped'] or not geometry['realized'] or geometry['gdkWindowReference'] is None:
        return None
    allocation = geometry['recipientAllocation']
    size = client['size']
    # This undecorated window has one full-size event window. Reject stale
    # client/GTK joins rather than treating requested geometry as delivered.
    if size != [geometry['windowAllocation']['width'], geometry['windowAllocation']['height']]:
        return None
    if [allocation['x'], allocation['y']] != [0, 0] or [allocation['width'], allocation['height']] != size:
        raise ValueError('Recipient is not the full allocated fixture surface')
    address = client.get('address')
    if not isinstance(address, str) or not address.startswith('0x'):
        raise ValueError('Missing observed native window address')
    return {'pid': pid, 'title': TITLE, 'address': address, 'at': list(client['at']),
            'size': list(size), 'geometry': geometry, 'sequence': latest['sequence'],
            'counts': latest['counts'], 'records': records}


def parent_point(observed, widget_point, child_monitor, parent_destination):
    if child_monitor.get('transform', 0) != 0:
        raise ValueError('Rotated monitor is outside this targeted probe')
    scale = child_monitor['scale']
    if not isinstance(scale, (int, float)) or not math.isfinite(scale) or scale <= 0:
        raise ValueError('Invalid observed child scale')
    child_width, child_height = child_monitor['width'] / scale, child_monitor['height'] / scale
    parent_width, parent_height = parent_destination
    values = [child_width, child_height, parent_width, parent_height, *widget_point]
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values) or min(values[:4]) <= 0:
        raise ValueError('Invalid observed coordinate bounds')
    x, y = widget_point
    if not 0 < x < observed['size'][0] or not 0 < y < observed['size'][1]:
        raise ValueError('Choose an interior allocated recipient point')
    child_x = observed['at'][0] - child_monitor['x'] + x
    child_y = observed['at'][1] - child_monitor['y'] + y
    if not 0 <= child_x < child_width or not 0 <= child_y < child_height:
        raise ValueError('Fixture point is outside the observed child monitor')
    return [child_x * parent_width / child_width, child_y * parent_height / child_height]


def delivered_since(observed, sequence, kind, expected_point=None, tolerance=2.0, button=None):
    matches = []
    for event in observed['records']:
        if event['sequence'] <= sequence or event['kind'] != kind:
            continue
        if (event.get('signalRecipient') != RECIPIENT or
                event.get('gdkEventWidget') != RECIPIENT or
                event.get('eventWindowWidget') != RECIPIENT or
                event.get('eventWindowReference') is None):
            raise ValueError('Event was not delivered to the declared recipient window')
        if button is not None and event.get('button') != button:
            continue
        if expected_point is not None and any(abs(event[key] - expected_point[index]) > tolerance for index, key in enumerate(('x', 'y'))):
            continue
        matches.append(event)
    return matches
