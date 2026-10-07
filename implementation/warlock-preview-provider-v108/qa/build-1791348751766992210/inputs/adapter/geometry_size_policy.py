"""Strict observation2 policy. Native authority alone performs mutations."""
import math
import sys
from endpoint import Refused, exact

MAX_INT = (1 << 31) - 1

def vector(value, nonnegative=True):
    if type(value) is not list or len(value) != 2:
        raise Refused('Geometry size vector')
    try:
        valid = all(type(v) in (int, float) and math.isfinite(v) and (not nonnegative or v >= 0) for v in value)
    except OverflowError:
        valid = False
    if not valid:
        raise Refused('Geometry size values')
    return value

def box(value):
    if type(value) is not list or len(value) != 4:
        raise Refused('Prospective box shape')
    vector(value[:2], False); vector(value[2:])
    if value[2] <= 0 or value[3] <= 0 or any(abs(v) > MAX_INT for v in value):
        raise Refused('Prospective box range')
    return value

def round_native(v):
    return (math.floor(v) + (v - math.floor(v) >= .5)) if v >= 0 else (math.ceil(v) - (math.ceil(v) - v >= .5))

def rounded(value):
    x, y, w, h = box(value)
    return [round_native(x), round_native(y), round_native(x + w) - round_native(x), round_native(y + h) - round_native(y)]

def valid_interval(lower, upper, raw):
    return all((raw and hi == 0) or (hi > 0 and lo < hi) for lo, hi in zip(lower, upper))

def fixed(inputs):
    for axis in range(2):
        lower = max(1, math.ceil(inputs['rawMinimum'][axis]), math.floor(inputs['layoutMinimum'][axis]))
        raw_upper = inputs['rawMaximum'][axis]
        upper = min(MAX_INT, math.floor(raw_upper) if raw_upper else MAX_INT, math.floor(inputs['layoutMaximum'][axis]))
        if lower >= upper:
            return True
    return False

def validate(policy, row):
    exact(policy, ['inputs', 'maximize', 'restoreGeometry'])
    inputs = policy['inputs']
    if inputs is None:
        if policy['maximize'] is not None or policy['restoreGeometry'] is not None:
            raise Refused('Projection without size observations')
        return False
    exact(inputs, ['profile', 'rawMinimum', 'rawMaximum', 'layoutMinimum', 'layoutMaximum',
                   'geometryOrigin', 'reservedTopLeft', 'reservedBottomRight', 'monitorScale'])
    if inputs['profile'] != 'wayland-zero-origin-v1':
        raise Refused('Unsupported geometry conversion profile')
    for field in ('rawMinimum', 'rawMaximum', 'layoutMinimum', 'layoutMaximum', 'reservedTopLeft', 'reservedBottomRight'):
        vector(inputs[field])
    vector(inputs['geometryOrigin'], False)
    scale = inputs['monitorScale']
    if type(scale) not in (int, float) or not math.isfinite(scale) or scale <= 0:
        raise Refused('Geometry scale')
    if not valid_interval(inputs['rawMinimum'], inputs['rawMaximum'], True) or not valid_interval(inputs['layoutMinimum'], inputs['layoutMaximum'], False):
        raise Refused('Invalid size intervals')
    constrained = (any(v > 1 for v in inputs['rawMinimum'] + inputs['layoutMinimum']) or
                   any(v > 0 for v in inputs['rawMaximum']) or any(v < sys.float_info.max for v in inputs['layoutMaximum']))
    is_fixed = fixed(inputs)
    if row['constrainedSize'] != constrained or row['fixedSize'] != is_fixed:
        raise Refused('Size state contradicts observed bounds')
    supported = inputs['geometryOrigin'] == [0, 0] and not is_fixed
    for operation in ('maximize', 'restoreGeometry'):
        projection = policy[operation]
        if projection is None:
            continue
        if not supported:
            raise Refused('Unsupported prospective conversion')
        exact(projection, ['logical', 'visual', 'real', 'configure'])
        logical = box(projection['logical']); real = box(projection['real'])
        if logical != rounded(logical):
            raise Refused('Unrounded prospective logical box')
        if projection['visual'] is not None:
            visual = box(projection['visual'])
            if visual != rounded(visual):
                raise Refused('Unrounded prospective visual box')
        configure = vector(projection['configure'])
        if configure != [math.floor(real[2]), math.floor(real[3])] or any(v < 1 or v > MAX_INT for v in configure):
            raise Refused('Prospective configure conversion')
        if operation == 'maximize':
            if row['workArea'] is None or logical != rounded(row['workArea']) or projection['visual'] is not None:
                raise Refused('Prospective workarea mismatch')
            tl, br = inputs['reservedTopLeft'], inputs['reservedBottomRight']
            expected = [logical[0] + tl[0], logical[1] + tl[1], logical[2] - (tl[0] + br[0]), logical[3] - (tl[1] + br[1])]
        else:
            expected = logical
            if projection['visual'] != real:
                raise Refused('Restore original visual mismatch')
        if real != expected:
            raise Refused('Prospective real conversion')
        for axis in range(2):
            raw_lo, raw_hi = inputs['rawMinimum'][axis], inputs['rawMaximum'][axis]
            lo, hi = inputs['layoutMinimum'][axis], inputs['layoutMaximum'][axis]
            if configure[axis] < raw_lo or (raw_hi and configure[axis] > raw_hi) or real[axis + 2] < lo or real[axis + 2] > hi:
                raise Refused('Infeasible prospective size')
    return supported
