"""Strict schema2 decoder for this exact core/plugin pair; no core/input effects.

All scalar types are exact (Python bool is never an integer). Decimal geometry
strings preserve the native serializer projection. This report is observations,
not authority to alter any target, compositor or focus.
"""
import json
import math
import re

class Refusal(ValueError):
    pass

def _require(condition, reason):
    if not condition:
        raise Refusal(reason)

def _object(value, keys):
    _require(type(value) is dict and set(value) == set(keys), "exact object schema")

def _integer(value, lower, upper):
    _require(type(value) is int and lower <= value <= upper, "exact bounded integer")

def _string(value):
    _require(type(value) is str, "exact string")

def _decimal(value, positive=False):
    _require(type(value) is str and re.fullmatch(r"0|[1-9][0-9]*", value) is not None, "exact decimal string")
    _require(int(value) <= 2**64-1 and (not positive or int(value)>0), "bounded generation")

def _pointer(value):
    _require(type(value) is str and re.fullmatch(r"0x(?:0|[1-9a-f][0-9a-f]*)", value) is not None and int(value,16)<=2**64-1, "exact pointer")

def _geometry(value, count):
    _require(type(value) is list and len(value)==count, "exact geometry length")
    for component in value:
        _require(type(component) is str and re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?",component) is not None, "decimal geometry string")
        _require(math.isfinite(float(component)), "finite geometry")

BOOLS="live normal floating pinned fullscreen nativeAdmission ownedUnpinReady restoreKnown restoreOrigin restoreManaged restoreFloating layoutHandled".split()
SNAPSHOT="address stableId pid epoch generation session incarnation internalMode clientMode capability restoreGeneration target layoutTarget space workspace monitor geometry restoreGeometry".split()+BOOLS

def snapshot(value):
    _object(value,SNAPSHOT)
    for key in BOOLS:
        _require(type(value[key]) is bool,"exact bool "+key)
    for key in ["address","target","layoutTarget","space","workspace","monitor"]:
        _pointer(value[key])
    _require(type(value["stableId"]) is str and re.fullmatch(r"0|[1-9a-f][0-9a-f]*",value["stableId"]) is not None and int(value["stableId"],16)<=2**64-1,"stable ID")
    _integer(value["pid"],0,2**31-1)
    for key in ["epoch","generation","restoreGeneration"]:
        _decimal(value[key])
    for key in ["session","incarnation"]:
        _string(value[key])
    for key in ["internalMode","clientMode"]:
        _integer(value[key],0,3)
    _integer(value["capability"],1,1)
    _geometry(value["geometry"],4);_geometry(value["restoreGeometry"],8)
    return value

def _pairs(pairs):
    value={}
    for key,item in pairs:
        _require(key not in value,"duplicate JSON key")
        value[key]=item
    return value

def decode(raw,expected_build):
    _require(type(raw) is bytes and 0<len(raw)<=65536,"bounded report bytes")
    _require(type(expected_build) is str and re.fullmatch(r"[0-9a-f]{64}",expected_build) is not None,"exact selected core source identity")
    try:
        report=json.loads(raw.decode("utf-8"),object_pairs_hook=_pairs,parse_constant=lambda _: (_ for _ in ()).throw(Refusal("non JSON scalar")))
    except (UnicodeError,json.JSONDecodeError) as error:
        raise Refusal("invalid JSON") from error
    _object(report,"schema corePolicyBuild ok phase reason actionsInvoked possiblePartialOutcome captured before after desiredPinned backend".split())
    _integer(report["schema"],2,2)
    _require(type(report["corePolicyBuild"]) is str and report["corePolicyBuild"]==expected_build,"selected core build")
    for key in ["ok","actionsInvoked","possiblePartialOutcome","desiredPinned"]:
        _require(type(report[key]) is bool,"exact report bool")
    _require(type(report["phase"]) is str and report["phase"] in {"validate","float","pin","raise","complete"},"known action phase")
    _string(report["reason"])
    _require(report["possiblePartialOutcome"] == (not report["ok"] and report["actionsInvoked"]),"truthful partial flag")
    _object(report["backend"],["ok","message","level","code"])
    _require(type(report["backend"]["ok"]) is bool,"exact backend bool")
    for key in ["message","level","code"]:_string(report["backend"][key])
    before=snapshot(report["before"]);after=snapshot(report["after"])
    captured=report["captured"]
    if captured is not None:
        _object(captured,"address stableId pid session compositorPid compositorStart incarnation epoch generation".split())
        _pointer(captured["address"])
        _require(type(captured["stableId"]) is str and captured["stableId"]==before["stableId"],"captured stable identity")
        for key in ["pid","compositorPid"]:_integer(captured[key],1,2**31-1)
        for key in ["compositorStart","epoch","generation"]:_decimal(captured[key],True)
        for key in ["session","incarnation"]:_string(captured[key])
        for key in ["address","stableId","pid","session","incarnation","epoch","generation"]:
            _require(captured[key]==before[key],"captured owner equality")
    if report["ok"]:
        _require(captured is not None and report["phase"]=="complete" and report["actionsInvoked"] and report["backend"]["ok"],"complete successful native report")
        for key in ["address","stableId","pid","epoch","generation","session","incarnation"]:
            _require(before[key]==after[key],"current owner equality")
        _require(after["live"] and after["normal"] and after["pinned"]==report["desiredPinned"] and report["desiredPinned"]!=before["pinned"],"selected intent transition")
        if before["nativeAdmission"] or before["ownedUnpinReady"]:
            _require(all(int(before[k],16)>0 for k in ["target","layoutTarget","space","workspace","monitor"]) and int(before["restoreGeneration"])>0,"current native owning tokens")
            _require(float(before["geometry"][2])>0 and float(before["geometry"][3])>0,"positive native displayed dimensions")
            if before["nativeAdmission"]:
                _require(before["restoreKnown"] and before["internalMode"]<=1 and before["clientMode"]<=1 and (before["internalMode"]==1 or before["restoreOrigin"]),"native admission projection")
                _require(float(before["restoreGeometry"][2])>0 and float(before["restoreGeometry"][3])>0,"positive native normal return dimensions")
            if before["ownedUnpinReady"]:
                _require(before["pinned"] and before["restoreOrigin"] and before["restoreManaged"] and not report["desiredPinned"],"owned explicit unpin projection")
            for key in ["internalMode","clientMode","fullscreen","floating","capability","restoreKnown","restoreGeneration","restoreFloating","layoutHandled","target","layoutTarget","space","workspace","monitor","geometry","restoreGeometry"]:
                _require(before[key]==after[key],"native context/return observation conservation")
            _require(after["restoreOrigin"]==report["desiredPinned"] and after["restoreManaged"],"owned intent result")
            if not report["desiredPinned"]:_require(not after["ownedUnpinReady"],"unpin consumed intent")
        else:
            _require(not before["restoreOrigin"] and before["internalMode"]==0 and not before["fullscreen"] and after["floating"] and after["internalMode"]==before["internalMode"] and after["clientMode"]==before["clientMode"],"ordinary pin conservation")
    return report
