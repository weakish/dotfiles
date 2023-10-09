#!/usr/bin/env python3

from typing import Callable, Sequence
import sys
if sys.version_info < (3, 8):
    raise Exception("Python 3.8 or higher is required.")
elif sys.version_info < (3, 9):
    pass
else:
    from typing import TypeAlias

import subprocess
from pathlib import Path
from myconfig import user, User

DOIT_CONFIG = {'action_string_formatting': 'both'}

if sys.version_info < (3, 10):
    from typing import Dict, Union
    DoItTask = Dict[str, Sequence[Union[str, Path, Callable]]]
else:
    DoItTask: TypeAlias = dict[str, Sequence[str | Path | Callable]]

def task_git() -> DoItTask:
    return {
            'file_dep': ['.gitconfig'],
            'actions': ['cp .gitconfig ~/.gitconfig'],
            'targets': [Path('~/.gitconfig').expanduser()],
            }

def run_git_config() -> None:
    for k in ('name', 'email', 'signingKey', 'github'):
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

def task_copy_dotfiles():
    for f in ['.hgrc', '.vimrc', '.zprofile']:
        yield {'basename': f[1:],
                'file_dep': [f],
                'actions': [f'cp {f} ~/{f}'],
                'targets': [Path(f'~/{f}').expanduser()],
                }


if __name__ == '__main__':
    import doit
    doit.run(globals())
