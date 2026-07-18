#!/usr/bin/env python3

import sys

if sys.version_info < (3, 10):
    raise Exception("Python 3.10 or higher is required.")

import subprocess
from pathlib import Path
from typing import Callable, Sequence, TypeAlias

from myconfig import user

DOIT_CONFIG = {'action_string_formatting': 'both'}

DoItTask: TypeAlias = dict[str, Sequence[str | Path | Callable]]


def task_git() -> DoItTask:
    return {
        'file_dep': ['.gitconfig', '.config/git/allowed_signers'],
        'actions': ['cp .gitconfig ~/.gitconfig', 'mkdir -p ~/.config/git',
                    'cp .config/git/allowed_signers ~/.config/git/allowed_signers'],
        'targets': [Path('~/.gitconfig').expanduser(), Path('~/.config/git/allowed_signers').expanduser()],
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


def task_git_personal() -> DoItTask:
    return {
        'task_dep': ['git'],
        'actions': [run_git_config]
    }


def task_hg() -> DoItTask:
    return {
        'file_dep': ['.hgrc'],
        'actions': ['cp .hgrc ~/.hgrc'],
        'targets': [Path('~/.hgrc').expanduser()],
    }


def task_hg_personal() -> DoItTask:
    def config_hg() -> None:
        name = user.get('name')
        email = user.get('email')
        if name is None:
            pass
        else:
            if email is None:
                username = name
            else:
                username = f'{name} <{email}>'
            with open(Path('~/.hgrc').expanduser(), 'a') as f:
                f.write(f'\n[ui]\nusername = {username}\n')

    return {
        'file_dep': ['.hgrc'],
        'task_dep': ['hg'],
        'actions': [config_hg],
    }

def task_paperwm() -> DoItTask:
    return {
        'file_dep': ['.hammerspoon/init.lua'],
        'actions': ['mkdir -p ~/.hammerspoon/Spoons',
                    'cp .hammerspoon/init.lua ~/.hammerspoon/init.lua',
                    'git -C ~/.hammerspoon/Spoons/PaperWM.spoon pull || git clone https://github.com/mogenson/PaperWM.spoon ~/.hammerspoon/Spoons/PaperWM.spoon'],
        'targets': [Path('~/.hammerspoon/Spoons/PaperWM.spoon').expanduser()],
    }

def task_copy_dotfiles():
    for f in ['.vimrc', '.zprofile', '.zshrc']:
        yield {'basename': f[1:],
               'file_dep': [f],
               'actions': [f'cp {f} ~/{f}'],
               'targets': [Path(f'~/{f}').expanduser()],
               }


if __name__ == '__main__':
    import doit

    doit.run(globals())
