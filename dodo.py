#!/usr/bin/env python3

import sys

if sys.version_info < (3, 10):
    raise Exception("Python 3.10 or higher is required.")

import shutil
import stat
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TypeAlias

from myconfig import user

DOIT_CONFIG = {"action_string_formatting": "both"}

DoItTask: TypeAlias = dict[str, Sequence[str | Path | Callable]]

MACOS = sys.platform == "darwin"


def task_herdr() -> DoItTask:
    return {
        "file_dep": [".config/herdr/config.toml"],
        "actions": [
            "mkdir -p ~/.config/herdr",
            "cp .config/herdr/config.toml ~/.config/herdr/config.toml",
        ],
        "targets": [Path("~/.config/herdr/config.toml").expanduser()],
    }


def task_skills() -> DoItTask:
    source = Path(".agents/skills").resolve()
    install_dir = Path("~/.agents/skills").expanduser()

    def relative_files(root: Path) -> list[Path]:
        return sorted(p.relative_to(root) for p in root.rglob("*") if p.is_file())

    def same_file(left: Path, right: Path) -> bool:
        return (
            stat.S_IMODE(left.stat().st_mode) == stat.S_IMODE(right.stat().st_mode)
            and left.read_bytes() == right.read_bytes()
        )

    def identical(left: Path, right: Path) -> bool:
        if right.is_symlink() or not right.is_dir():
            return False
        names = relative_files(left)
        return names == relative_files(right) and all(
            same_file(left / name, right / name) for name in names
        )

    def synced() -> bool:
        return source.is_dir() and identical(source, install_dir)

    def replace_skills() -> None:
        if not source.is_dir():
            raise RuntimeError(
                f"refusing to replace {install_dir}, {source} is missing"
            )
        # Resolve only the parent: a symlinked install dir is unlinked, not followed.
        location = install_dir.parent.resolve() / install_dir.name
        if source.is_relative_to(location) or location.is_relative_to(source):
            raise RuntimeError(
                f"refusing to replace {install_dir}, which overlaps {source}"
            )
        if install_dir.is_symlink() or install_dir.is_file():
            install_dir.unlink()
        elif install_dir.is_dir():
            shutil.rmtree(install_dir)
        shutil.copytree(source, install_dir)

    return {"actions": [replace_skills], "uptodate": [synced]}


if MACOS:

    def task_git() -> DoItTask:
        return {
            "file_dep": [".gitconfig", ".config/git/allowed_signers"],
            "actions": [
                "cp .gitconfig ~/.gitconfig",
                "mkdir -p ~/.config/git",
                "cp .config/git/allowed_signers ~/.config/git/allowed_signers",
            ],
            "targets": [
                Path("~/.gitconfig").expanduser(),
                Path("~/.config/git/allowed_signers").expanduser(),
            ],
        }

    def run_git_config() -> None:
        for k in ("name", "email", "signingKey", "github"):
            v = user.get(k)
            if v is None:
                pass
            else:
                if k == "github":
                    subprocess.run(["git", "config", "--global", "github.user", v])
                else:
                    subprocess.run(["git", "config", "--global", f"user.{k}", v])

    def task_git_personal() -> DoItTask:
        return {"task_dep": ["git"], "actions": [run_git_config]}

    def task_hg() -> DoItTask:
        return {
            "file_dep": [".hgrc"],
            "actions": ["cp .hgrc ~/.hgrc"],
            "targets": [Path("~/.hgrc").expanduser()],
        }

    def task_hg_personal() -> DoItTask:
        def config_hg() -> None:
            name = user.get("name")
            email = user.get("email")
            if name is None:
                pass
            else:
                if email is None:
                    username = name
                else:
                    username = f"{name} <{email}>"
                with open(Path("~/.hgrc").expanduser(), "a") as f:
                    f.write(f"\n[ui]\nusername = {username}\n")

        return {
            "file_dep": [".hgrc"],
            "task_dep": ["hg"],
            "actions": [config_hg],
        }

    def task_kitty() -> DoItTask:
        return {
            "file_dep": [".config/kitty/kitty.conf"],
            "actions": [
                "mkdir -p ~/.config/kitty",
                "cp .config/kitty/kitty.conf ~/.config/kitty/kitty.conf",
            ],
            "targets": [Path("~/.config/kitty/kitty.conf").expanduser()],
        }

    def task_paperwm() -> DoItTask:
        return {
            "file_dep": [".hammerspoon/init.lua"],
            "actions": [
                "mkdir -p ~/.hammerspoon/Spoons",
                "cp .hammerspoon/init.lua ~/.hammerspoon/init.lua",
                "git -C ~/.hammerspoon/Spoons/PaperWM.spoon pull || "
                "git clone https://github.com/mogenson/PaperWM.spoon "
                "~/.hammerspoon/Spoons/PaperWM.spoon",
            ],
            "targets": [Path("~/.hammerspoon/Spoons/PaperWM.spoon").expanduser()],
        }


def task_copy_dotfiles():
    files = [".vimrc"]
    if MACOS:
        files.extend([".zprofile", ".zshrc"])
    for f in files:
        yield {
            "basename": f[1:],
            "file_dep": [f],
            "actions": [f"cp {f} ~/{f}"],
            "targets": [Path(f"~/{f}").expanduser()],
        }


if __name__ == "__main__":
    import doit

    doit.run(globals())
