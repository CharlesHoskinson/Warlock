from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from helper_supervisor import Keeper
from owned_commands import OwnedCommands

class OwnedCommandTests(unittest.TestCase):
    def setup(self,raw,writer=lambda body:None):
        root=Path(raw);env=dict(os.environ,XDG_RUNTIME_DIR=str(root),HYPRLAND_INSTANCE_SIGNATURE='offline',WAYLAND_DISPLAY='never-connect')
        keeper=Keeper(root,env,writer);return root,keeper,OwnedCommands(keeper,env,17)
    def finish(self,keeper):
        if keeper.process.poll() is None:
            if not keeper.jobs:keeper.stop()
            else:keeper.detach();keeper.process.wait(timeout=5);keeper.process.stderr.close()
    def test_python_keeps_exact_file_argv_and_import_directory(self):
        with tempfile.TemporaryDirectory() as raw:
            root,keeper,commands=self.setup(raw)
            try:
                (root/'localmodule.py').write_text('VALUE=73\n')
                path=root/'observer';path.write_text('#!/usr/bin/env python3\nimport json,sys,localmodule\nprint(json.dumps([__file__,sys.argv,localmodule.VALUE]))\n');path.chmod(0o500)
                result=commands.check_output([str(path),'literal $() arg'],text=True,timeout=2)
                self.assertEqual(json.loads(result),[str(path),[str(path),'literal $() arg'],73])
            finally:self.finish(keeper)
    def test_bash_keeps_zero_and_literal_argument_vector(self):
        with tempfile.TemporaryDirectory() as raw:
            root,keeper,commands=self.setup(raw)
            try:
                path=root/'core';path.write_text('#!/usr/bin/env bash\nset -euo pipefail\nprintf "%s\\n" "$0" "$1" "$2"\n');path.chmod(0o500)
                output=commands.check_output([str(path),'$(must-not-run)','arg with spaces'],text=True,timeout=2)
                self.assertEqual(output.splitlines(),[str(path),'$(must-not-run)','arg with spaces'])
            finally:self.finish(keeper)
    def test_source_replacement_after_gated_record_does_not_change_executed_bytes(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);path=root/'observer';path.write_text('#!/usr/bin/env python3\nprint("ORIGINAL")\n');path.chmod(0o500)
            changed=[]
            def writer(body):
                if body['jobs'] and body['jobs'][0]['phase']=='gated' and not changed:
                    path.chmod(0o700);path.write_text('#!/usr/bin/env python3\nprint("REPLACED")\n');changed.append(True)
            root,keeper,commands=self.setup(raw,writer)
            try:self.assertEqual(commands.check_output([str(path)],text=True,timeout=2),'ORIGINAL\n');self.assertTrue(changed)
            finally:self.finish(keeper)
    def test_unsupported_source_introspection_refuses_before_registration(self):
        with tempfile.TemporaryDirectory() as raw:
            root,keeper,commands=self.setup(raw)
            try:
                path=root/'core';path.write_text('#!/bin/bash\necho "$BASH_SOURCE"\n');path.chmod(0o500)
                with self.assertRaisesRegex(ValueError,'explicit adapter'):commands.run([str(path)])
                self.assertFalse(keeper.jobs)
            finally:self.finish(keeper)
    def test_selected_environment_change_refuses_before_process(self):
        with tempfile.TemporaryDirectory() as raw:
            root,keeper,commands=self.setup(raw)
            try:
                with self.assertRaisesRegex(ValueError,'session environment'):commands.run(['/usr/bin/true'],env=dict(commands.env,WAYLAND_DISPLAY='wrong'))
                self.assertFalse(keeper.jobs)
            finally:self.finish(keeper)
    def test_nonzero_helper_returncode_keeps_standard_check_semantics(self):
        with tempfile.TemporaryDirectory() as raw:
            root,keeper,commands=self.setup(raw)
            try:
                with self.assertRaises(subprocess.CalledProcessError):commands.check_output(['/usr/bin/false'],timeout=2)
                self.assertFalse(keeper.jobs)
            finally:self.finish(keeper)

    def test_actual_foreground_timeout_preserves_deadline_and_original_arguments(self):
        with tempfile.TemporaryDirectory() as raw:
            root,keeper,commands=self.setup(raw)
            try:
                path=root/'deadline';path.write_text('#!/bin/bash\ntimeout --kill-after=.1s .02s /usr/bin/sleep 5\n');path.chmod(0o500)
                result=commands.run([str(path)],capture_output=True,text=True,timeout=2)
                self.assertEqual(result.returncode,124,result.stderr);self.assertFalse(keeper.jobs)
            finally:self.finish(keeper)
    def test_original_default_timeout_counterexample_kills_owned_group_on_expiry(self):
        import sys
        script='from helper_policy import install; import subprocess; install(); r=subprocess.run(["/usr/bin/timeout",".02s","/usr/bin/sleep","5"],capture_output=True,text=True); print(r.returncode); print(r.stderr)'
        result=subprocess.run([sys.executable,'-c',script],cwd=Path(__file__).parent,start_new_session=True,capture_output=True,text=True,timeout=2)
        self.assertEqual(result.returncode,-15,result.stderr)
    def test_confined_timeout_function_survives_nested_bash_exec(self):
        with tempfile.TemporaryDirectory() as raw:
            root,keeper,commands=self.setup(raw)
            try:
                path=root/'outer';path.write_text('#!/bin/bash\n/usr/bin/bash -c \'timeout 1s /usr/bin/true\'\n');path.chmod(0o500)
                result=commands.run([str(path)],capture_output=True,text=True,timeout=2)
                self.assertEqual(result.returncode,0,result.stderr);self.assertFalse(keeper.jobs)
            finally:self.finish(keeper)

if __name__=='__main__':unittest.main()
