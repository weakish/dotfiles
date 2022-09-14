#!/usr/bin/env python3

from __future__ import annotations
from typing import Callable, Sequence
import sys
if sys.version_info < (3, 7):
    raise Exception("Python 3.7 or higher is required.")
elif sys.version_info < (3, 9):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

import subprocess
from pathlib import Path
from myconfig import user, User

DOIT_CONFIG = {'action_string_formatting': 'both'}

DoItTask: TypeAlias = dict[str, Sequence[str | Path | Callable]]

def task_git() -> DoItTask:
    return {
            'file_dep': ['.gitconfig'],
            'actions': ['cp .gitconfig ~/.gitconfig'],
            'targets': [Path('~/.gitconfig').expanduser()],
            }

def run_git_config() -> None:
    for k in ('name', 'email', 'signingkey', 'github'):
        v = user.get(k)
        if v is None:
            pass
        else:
            if k == 'github':
                subprocess.run(['git', 'config', '--global', 'github.user', user['github']])
            else:
                subprocess.run(['git', 'config', '--global', f'user.{k}', v])

def task_git_persnoal() -> DoItTask:
    return {
            'file_dep': ['.gitconfig'],
            'task_dep': ['git'],
            'actions': [run_git_config]
            }


def task_vim() -> DoItTask:
    return {
            'file_dep': ['.vimrc'],
            'actions': ['cp .vimrc ~/.vimrc'],
            'targets': [Path('~/.vimrc').expanduser()]
            }

def task_hg() -> DoItTask:
    return {
            'file_dep': ['.hgrc'],
            'actions': ['cp .hgrc ~/.hgrc'],
            'targets': [Path('~/.hgrc').expanduser()],
            }

if __name__ == '__main__':
    import doit
    doit.run(globals())
