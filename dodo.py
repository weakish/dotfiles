#!/usr/bin/env python3

from pathlib import Path

DOIT_CONFIG = {'action_string_formatting': 'both'}

def task_vim():
    return {
            'file_dep': ['.vimrc'],
            'actions': ['cp .vimrc ~/.vimrc'],
            'targets': [Path('~/.vimrc').expanduser()]
            }

def task_hg():
    return {
            'file_dep': ['.hgrc'],
            'actions': ['cp .hgrc ~/.hgrc'],
            'targets': [Path('~/.hgrc').expanduser()],
            }

if __name__ == '__main__':
    import doit
    doit.run(globals())
