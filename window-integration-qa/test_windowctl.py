#!/usr/bin/env python3
"""Exercise the real windowctl script against a small stateful Hyprland mock."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


WINDOWCTL = Path("/home/hoskinson/.local/bin/hypr-windowctl")
DESKTOP = Path("/home/hoskinson/.local/bin/hypr-desktop")
VIRTUAL_DESKTOPS = Path("/home/hoskinson/.local/bin/hypr-desktops")
MOCK_HYPRCTL = r'''#!/usr/bin/env python3
import json, os, re, sys
from pathlib import Path
p = Path(os.environ["WINDOWCTL_MOCK_STATE"])
s = json.loads(p.read_text())
args = sys.argv[1:]
if args == ["clients", "-j"]:
    print(json.dumps(s["clients"]))
elif args == ["activewindow", "-j"]:
    print(json.dumps({"address": s["active"]}))
elif args == ["monitors", "-j"]:
    print(json.dumps(s.get("monitors", [{"id":0,"name":"physical","focused": True, "activeWorkspace": {"name": s["workspace"]}}])))
elif args == ["workspaces", "-j"]:
    print(json.dumps(s.get("workspaces", [{"name":s["workspace"],"monitorID":0,"monitor":"physical"}])))
elif args[:1] == ["getprop"]:
    prop = args[2]
    default = {"opacity": "1", "opacity_inactive": "0.96",
               "opacity_fullscreen": "1", "opacity_override": "false",
               "opacity_inactive_override": "false",
               "opacity_fullscreen_override": "false"}
    print(s.get("props", {}).get(args[1], {}).get(prop, default[prop]))
elif args[:1] == ["dispatch"]:
    cmd = args[1]
    address = re.search(r'window = "address:(0x[0-9a-fA-F]+)"', cmd)
    window = next((w for w in s["clients"] if address and w["address"] == address.group(1)), None)
    if "hl.dsp.window.pin(" in cmd and window:
        window["pinned"] = not window["pinned"]
    elif "hl.dsp.window.set_prop(" in cmd and window:
        prop = re.search(r'prop = "([^"]+)"', cmd).group(1)
        value = re.search(r'value = "([^"]+)"', cmd).group(1)
        s.setdefault("props", {}).setdefault(address.group(0).split('"')[1], {})[prop] = value
    elif "hl.dsp.window.move(" in cmd and window:
        ws = re.search(r'workspace = "([^"]+)"', cmd)
        window["workspace"] = {"name": ws.group(1)}
        if "monitor" in window:
            owners={w['name']:w['monitorID'] for w in s.get('workspaces',[])}
            window['monitor']=0 if ws.group(1).startswith('special:') else owners.get(ws.group(1),s.get('activeMonitor',0))
    elif "hl.dsp.focus(" in cmd:
        ws = re.search(r'workspace = "([^"]+)"', cmd)
        target = re.search(r'window = "address:(0x[0-9a-fA-F]+)"', cmd)
        if ws: s["workspace"] = ws.group(1)
        if target: s["active"] = target.group(1)
        monitor=re.search(r'monitor = "([^"]+)"',cmd)
        if monitor:s['activeMonitor']=next(m['id'] for m in s.get('monitors',[{'id':0,'name':'physical'}]) if m['name']==monitor.group(1))
    s["dispatches"].append(cmd)
    p.write_text(json.dumps(s))
    print("ok")
else:
    sys.exit(2)
'''


def window(address, workspace="1", pinned=False, stable_id=""):
    return {"address": address, "mapped": True, "pinned": pinned,
            "workspace": {"name": workspace}, "stableId": stable_id}


class Environment:
    def __init__(self, clients, active="0xaaa", workspace="1"):
        self.temp = tempfile.TemporaryDirectory(prefix="windowctl-qa-")
        self.root = Path(self.temp.name)
        (self.root / "bin").mkdir()
        (self.root / "home/.local/bin").mkdir(parents=True)
        (self.root / "runtime").mkdir()
        mock = self.root / "bin/hyprctl"
        mock.write_text(MOCK_HYPRCTL)
        mock.chmod(0o755)
        preview = self.root / "home/.local/bin/hypr-window-preview"
        preview.write_text("#!/bin/sh\nexit 0\n")
        preview.chmod(0o755)
        shutil.copy2(WINDOWCTL, self.root / "home/.local/bin/hypr-windowctl")
        core=WINDOWCTL.with_name("hypr-windowctl-core")
        if core.exists():shutil.copy2(core,self.root / "home/.local/bin/hypr-windowctl-core")
        self.state_path = self.root / "state.json"
        self.state_path.write_text(json.dumps({"clients": clients, "active": active,
                                              "workspace": workspace, "dispatches": []}))
        self.env = dict(os.environ, PATH=str(self.root / "bin") + ":" + os.environ["PATH"],
                        HOME=str(self.root / "home"), XDG_CONFIG_HOME=str(self.root / "home/.config"),
                        XDG_RUNTIME_DIR=str(self.root / "runtime"),
                        WINDOWCTL_MOCK_STATE=str(self.state_path), HYPR_WINDOWCTL_MOTION="0")

    def run(self, *args, expected=0):
        result = subprocess.run([str(WINDOWCTL), *args], env=self.env,
                                text=True, capture_output=True)
        assert result.returncode == expected, (args, result.returncode, result.stderr)
        return self.state

    def desktop(self, *args, expected=0):
        result = subprocess.run([str(DESKTOP), *args], env=self.env,
                                text=True, capture_output=True)
        assert result.returncode == expected, (args, result.returncode, result.stderr)
        return result.stdout, self.state

    def virtual_desktops(self, *args, expected=0):
        result = subprocess.run([str(VIRTUAL_DESKTOPS), *args], env=self.env,
                                text=True, capture_output=True)
        assert result.returncode == expected, (args, result.returncode, result.stderr)
        return json.loads(result.stdout) if result.stdout else None, self.state

    @property
    def state(self):
        return json.loads(self.state_path.read_text())

    def close(self):
        self.temp.cleanup()


def check_normal_restore():
    e = Environment([window("0xaaa")])
    try:
        s = e.run("minimize", "0xaaa")
        assert s["clients"][0]["workspace"]["name"] == "special:win-minimized"
        assert (e.root / "runtime/hypr-windowctl/0xaaa").read_text() == "1 0\n"
        s = e.run("restore", "0xaaa")
        assert s["clients"][0]["workspace"]["name"] == "1"
        assert s["active"] == "0xaaa"
    finally:
        e.close()


def check_minimized_monitor_metadata():
    e=Environment([dict(window('0xaaa','2',stable_id='42'),pid=23,monitor=7)])
    try:
        state=e.state
        state['monitors']=[dict(id=0,name='physical',focused=True,activeWorkspace={'id':1,'name':'1'}),dict(id=7,name='virtual',focused=False)]
        state['workspaces']=[dict(name='2',monitorID=7,monitor='virtual')]
        e.state_path.write_text(json.dumps(state))
        e.run('minimize','0xaaa')
        metadata=e.root/'runtime/hypr-windowctl/0xaaa.monitor.json'
        assert json.loads(metadata.read_text())==dict(pid=23,stableId='42',homeWorkspace='2',monitorName='virtual')
        state=e.state
        assert state['clients'][0]['monitor']==0
        state['workspaces']=[]
        e.state_path.write_text(json.dumps(state))
        state=e.run('restore','0xaaa')
        assert state['clients'][0]['monitor']==7
        assert not metadata.exists()
    finally:e.close()


def check_minimized_monitor_desktop_move():
    e=Environment([dict(window('0xaaa','2',stable_id='42'),pid=23,monitor=7)])
    try:
        state=e.state
        state['monitors']=[dict(id=0,name='physical',focused=True,activeWorkspace={'id':1,'name':'1'}),dict(id=7,name='virtual',focused=False)]
        state['workspaces']=[dict(name='1',monitorID=0,monitor='physical'),dict(name='2',monitorID=7,monitor='virtual')]
        e.state_path.write_text(json.dumps(state))
        e.run('minimize','0xaaa')
        e.virtual_desktops('move','0xaaa','1')
        saved=json.loads((e.root/'runtime/hypr-windowctl/0xaaa.monitor.json').read_text())
        assert saved['homeWorkspace']=='1' and saved['monitorName']=='physical'
        state=e.run('restore','0xaaa')
        assert state['clients'][0]['monitor']==0
    finally:e.close()


def check_pin_restore():
    e = Environment([window("0xaaa", "2", True)], workspace="2")
    try:
        s = e.run("minimize", "0xaaa")
        assert not s["clients"][0]["pinned"]
        s = e.run("restore", "0xaaa")
        assert s["clients"][0]["pinned"]
        assert s["clients"][0]["workspace"]["name"] == "2"
    finally:
        e.close()


def check_minimize_all():
    e = Environment([window("0xaaa"), window("0xbbb"),
                     window("0xccc", "special:scratchpad")])
    try:
        s = e.run("minimize-all")
        assert [w["workspace"]["name"] for w in s["clients"]] == [
            "special:win-minimized", "special:win-minimized", "special:scratchpad"]
        s = e.run("restore-all")
        assert [w["workspace"]["name"] for w in s["clients"]] == [
            "1", "1", "special:scratchpad"]
    finally:
        e.close()


def check_minimize_others_toggle():
    e = Environment([window("0xaaa"), window("0xbbb"), window("0xccc")])
    try:
        s = e.run("minimize-others")
        assert [w["workspace"]["name"] for w in s["clients"]] == [
            "1", "special:win-minimized", "special:win-minimized"]
        s = e.run("minimize-others")
        assert all(w["workspace"]["name"] == "1" for w in s["clients"])
        assert s["active"] == "0xaaa"
    finally:
        e.close()


def check_other_workspaces_untouched():
    e = Environment([window("0xaaa", "1"), window("0xbbb", "2"),
                     window("0xccc", "2", True)])
    try:
        s = e.run("minimize-all")
        assert [w["workspace"]["name"] for w in s["clients"]] == [
            "special:win-minimized", "2", "special:win-minimized"]
        s = e.run("restore-all")
        assert [w["workspace"]["name"] for w in s["clients"]] == ["1", "2", "2"]
        assert s["clients"][2]["pinned"]
        assert s["workspace"] == "1"
    finally:
        e.close()


def check_shake_owner_survives_focus_race():
    e = Environment([window("0xaaa", "1"), window("0xbbb", "2"),
                     window("0xccc", "1")], active="0xbbb", workspace="2")
    try:
        s = e.run("minimize-others", "0xaaa")
        assert [w["workspace"]["name"] for w in s["clients"]] == [
            "1", "2", "special:win-minimized"]
        s = e.run("minimize-others", "0xaaa")
        assert [w["workspace"]["name"] for w in s["clients"]] == ["1", "2", "1"]
    finally:
        e.close()


def check_shake_batches_are_per_workspace():
    e = Environment([window("0xaaa", "1"), window("0xbbb", "2"),
                     window("0xccc", "1"), window("0xddd", "2")])
    try:
        state = e.run("minimize-others", "0xaaa")
        assert state["clients"][2]["workspace"]["name"] == "special:win-minimized"
        state.update(active="0xbbb", workspace="2")
        e.state_path.write_text(json.dumps(state))
        state = e.run("minimize-others", "0xbbb")
        assert state["clients"][3]["workspace"]["name"] == "special:win-minimized"
        state = e.run("minimize-others", "0xbbb")
        assert state["clients"][3]["workspace"]["name"] == "2"
        assert state["clients"][2]["workspace"]["name"] == "special:win-minimized"
        state.update(active="0xaaa", workspace="1")
        e.state_path.write_text(json.dumps(state))
        state = e.run("minimize-others", "0xaaa")
        assert state["clients"][2]["workspace"]["name"] == "1"
    finally:
        e.close()


def check_legacy_and_invalid():
    e = Environment([window("0xaaa", "special:scratchpad")], workspace="3")
    try:
        e.run("minimize", "0xaaa")
        assert e.state["clients"][0]["workspace"]["name"] == "special:scratchpad"
        s = e.run("restore", "0xaaa")
        assert s["clients"][0]["workspace"]["name"] == "3"
        before = e.state
        e.run("restore", "0xaaa;touch /tmp/bad", expected=2)
        assert e.state == before
    finally:
        e.close()


def check_show_desktop_and_peek():
    e = Environment([window("0xaaa", "1"), window("0xbbb", "2"),
                     window("0xccc", "2", True)])
    try:
        output, _ = e.desktop("state")
        assert json.loads(output) == {"showing": False, "peeking": False}
        _, s = e.desktop("peek-on")
        tags = [x for x in s["dispatches"] if "+omarchy-peek" in x]
        assert len(tags) == 2 and all("0xbbb" not in x for x in tags)
        assert s["props"]["address:0xaaa"]["opacity"] == "0.03"
        output, _ = e.desktop("state")
        assert json.loads(output)["peeking"]
        _, s = e.desktop("peek-off")
        assert sum("-omarchy-peek" in x for x in s["dispatches"]) == 2
        assert s["props"]["address:0xaaa"]["opacity"] == "1"
        _, s = e.desktop("toggle")
        assert [w["workspace"]["name"] for w in s["clients"]] == [
            "special:win-minimized", "2", "special:win-minimized"]
        output, _ = e.desktop("state")
        assert json.loads(output)["showing"]
        _, s = e.desktop("toggle")
        assert [w["workspace"]["name"] for w in s["clients"]] == ["1", "2", "2"]
    finally:
        e.close()


def check_show_desktop_is_per_workspace():
    e = Environment([window("0xaaa", "1"), window("0xbbb", "2")])
    try:
        e.desktop("toggle")
        state = e.state
        state.update(active="0xbbb", workspace="2")
        e.state_path.write_text(json.dumps(state))
        status, _ = e.desktop("state")
        assert not json.loads(status)["showing"]
        _, state = e.desktop("toggle")
        assert all(w["workspace"]["name"] == "special:win-minimized"
                   for w in state["clients"])
        state["workspace"] = "1"
        state["active"] = "0xaaa"
        e.state_path.write_text(json.dumps(state))
        _, state = e.desktop("toggle")
        assert [w["workspace"]["name"] for w in state["clients"]] == [
            "1", "special:win-minimized"]
        state["workspace"] = "2"
        state["active"] = "0xbbb"
        e.state_path.write_text(json.dumps(state))
        _, state = e.desktop("toggle")
        assert [w["workspace"]["name"] for w in state["clients"]] == ["1", "2"]
    finally:
        e.close()


def check_batch_rejects_reused_address():
    e = Environment([window("0xaaa", stable_id="old")])
    try:
        state = e.run("minimize-all")
        state["clients"][0]["stableId"] = "new"
        e.state_path.write_text(json.dumps(state))
        state = e.run("restore-all")
        assert state["clients"][0]["workspace"]["name"] == "special:win-minimized"
    finally:
        e.close()


def check_window_restore_rejects_reused_address():
    e = Environment([window("0xaaa", "2", True, "old")], workspace="2")
    try:
        state = e.run("minimize", "0xaaa")
        state["clients"][0]["stableId"] = "new"
        state["workspace"] = "1"
        e.state_path.write_text(json.dumps(state))
        state = e.run("restore", "0xaaa")
        assert state["clients"][0]["workspace"]["name"] == "1"
        assert not state["clients"][0]["pinned"]
    finally:
        e.close()


def check_virtual_desktops():
    e = Environment([window("0xaaa", "1"), window("0xbbb", "2")])
    try:
        result, _ = e.virtual_desktops("list")
        assert [d["id"] for d in result["desktops"]] == ["1", "2"]
        result, s = e.virtual_desktops("new")
        assert result["active"] == "3" and s["workspace"] == "3"
        result, _ = e.virtual_desktops("rename", "3", "Writing")
        assert next(d for d in result["desktops"] if d["id"] == "3")["name"] == "Writing"
        result, _ = e.virtual_desktops("reorder", "3", "1")
        assert [d["id"] for d in result["desktops"]] == ["3", "1", "2"]
        result, _ = e.virtual_desktops("reorder", "3", "end")
        assert [d["id"] for d in result["desktops"]] == ["1", "2", "3"]
        result, _ = e.virtual_desktops("reorder", "3", "1")
        assert [d["id"] for d in result["desktops"]] == ["3", "1", "2"]
        _, s = e.virtual_desktops("move", "0xaaa", "3")
        assert s["clients"][0]["workspace"]["name"] == "3"
        result, s = e.virtual_desktops("close", "3")
        assert s["clients"][0]["workspace"]["name"] == "1"
        assert [d["id"] for d in result["desktops"]] == ["1", "2"]
        e.virtual_desktops("move", "0xbbb", "2")
        e.virtual_desktops("move", "0xbbb;bad", "1", expected=2)
    finally:
        e.close()


def check_new_desktop_with_dragged_window():
    e = Environment([window("0xaaa", "1"), window("0xbbb", "1")])
    try:
        e.run("minimize", "0xbbb")
        result, state = e.virtual_desktops("new-move", "0xbbb")
        assert result["active"] == "2"
        assert state["clients"][1]["workspace"]["name"] == "special:win-minimized"
        assert (e.root / "runtime/hypr-windowctl/0xbbb").read_text() == "2 0\n"
        state = e.run("restore", "0xbbb")
        assert state["clients"][1]["workspace"]["name"] == "2"
        result, state = e.virtual_desktops("new-move", "0xaaa")
        assert result["active"] == "3"
        assert state["clients"][0]["workspace"]["name"] == "3"
        e.virtual_desktops("new-move", "bad", expected=2)
    finally:
        e.close()


def check_task_view_rejects_stale_preview():
    w = window("0xaaa", stable_id="new")
    w["pid"] = 123
    e = Environment([w])
    try:
        cache = e.root / "runtime/hypr-window-previews"
        cache.mkdir()
        (cache / "0xaaa-0.png").write_bytes(b"preview")
        (cache / "0xaaa.json").write_text(json.dumps({"pid": 123, "stableId": "old"}))
        result, _ = e.virtual_desktops("list")
        assert result["desktops"][0]["windows"][0]["preview"] == ""
        (cache / "0xaaa.json").write_text(json.dumps({"pid": 123, "stableId": "new"}))
        result, _ = e.virtual_desktops("list")
        assert result["desktops"][0]["windows"][0]["preview"] == str(cache / "0xaaa-0.png")
    finally:
        e.close()


def check_close_desktop_retargets_minimized():
    e = Environment([window("0xaaa", "2", stable_id="old")], active="0xaaa", workspace="2")
    try:
        e.virtual_desktops("list")
        e.run("minimize-all")
        assert (e.root / "runtime/hypr-windowctl/minimize-all-2").exists()
        result, _ = e.virtual_desktops("close", "2")
        assert [d["id"] for d in result["desktops"]] == ["1"]
        assert (e.root / "runtime/hypr-windowctl/0xaaa").read_text() == "1 0 old\n"
        assert not (e.root / "runtime/hypr-windowctl/minimize-all-2").exists()
        s = e.run("restore", "0xaaa")
        assert s["clients"][0]["workspace"]["name"] == "1"
    finally:
        e.close()


def check_restore_requires_requested_identity():
    original=window("0xaaa",stable_id="live");original['pid']=123
    e=Environment([original],active="",workspace="1")
    try:
        s=e.run('restore','0xaaa','stale','123',expected=3)
        assert s['dispatches']==[]
        s=e.run('restore','0xaaa','live','124',expected=3)
        assert s['dispatches']==[]
        s=e.run('restore','0xaaa','live','123')
        assert s['active']=='0xaaa'
    finally:e.close()


if __name__ == "__main__":
    tests = (check_normal_restore, check_minimized_monitor_metadata, check_minimized_monitor_desktop_move, check_pin_restore, check_minimize_all,
                 check_minimize_others_toggle, check_other_workspaces_untouched,
                 check_shake_owner_survives_focus_race, check_shake_batches_are_per_workspace,
                 check_legacy_and_invalid,
                 check_show_desktop_and_peek, check_show_desktop_is_per_workspace,
                 check_batch_rejects_reused_address, check_window_restore_rejects_reused_address,
                 check_virtual_desktops, check_new_desktop_with_dragged_window,
                 check_task_view_rejects_stale_preview,
                 check_close_desktop_retargets_minimized, check_restore_requires_requested_identity)
    for test in tests:
        test()
    print(f"windowctl/desktop QA: {len(tests)} stateful scenarios passed")
