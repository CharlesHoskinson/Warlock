#!/usr/bin/env python3
"""Start the entire QA process tree in an isolated user scope."""
import argparse
import os
from pathlib import Path
import sys
import uuid
from qa_launch import require_qa_scope, runtime_base, verify_device_access


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backtrace', action='store_true', help='Explicitly enable diagnostic core dumps')
    parser.add_argument('--inside-scope', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == '--':
        command = command[1:]
    if not command:
        parser.error('expected -- <launcher> [arguments]')
    if args.inside_scope:
        require_qa_scope()
        runtime_base()
        verify_device_access()
        os.execvpe(command[0], command, os.environ)
    env = dict(os.environ)
    env.pop('WINDOW_QA_BACKTRACE', None)
    if args.backtrace:
        env['WINDOW_QA_BACKTRACE'] = '1'
    unit = 'qa-harness-' + uuid.uuid4().hex
    wrapper = [sys.executable, str(Path(__file__).resolve()), '--inside-scope', '--', *command]
    # LimitCORE is a service property: systemd 261 rejects it on scope units.
    # Apply the same inherited soft/hard limit before executing the harness.
    core = 'unlimited' if args.backtrace else '1'
    launch = ['systemd-run', '--user', '--scope', '--slice=qa-harness.slice',
              '--unit=' + unit, '--', 'prlimit', '--core=' + core + ':' + core, '--', *wrapper]
    os.execvpe(launch[0], launch, env)


if __name__ == '__main__':
    main()
