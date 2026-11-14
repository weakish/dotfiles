My dotfiles for macOS and Linux.

## Usage

Ensure that git is installed, then:

    git clone https://github.com/weakish/dotfiles
    cd dotfiles
    cp myconfig.example.py myconfig.py
    # edit myconfig.py
    sh script/setup

`script/setup` detects the platform:

- **macOS**: installs packages with MacPorts/Homebrew and applies the full desktop config.
- **Linux** (Debian/Ubuntu): installs `linux-packages.txt` with apt and applies the minimal headless dev VM config.

Linux keeps git at its defaults (no `.gitconfig`) and skips the macOS-only pieces: kitty, Hammerspoon/PaperWM, and `.zprofile`. It also skips `.hgrc` and `.zshrc`, because setup installs neither mercurial nor zsh on Linux.

Edit `linux-packages.txt` to add or remove apt packages.

## Features

- Vim in private mode.

- [Sign all git commits and tags][git-sign] with ssh key (macOS only).

    Git supports signing commits with a GPG, SSH, or X.509 key.
    I prefer the SSH key for signing because I mainly use ssh protocol to communite with git server, thus the ssh key is always available on the machine.

    Please edit `.config/git/allowed_signers` to add your trusted ssh public keys.

[git-sign]: https://blog.gitbutler.com/signing-commits-in-git-explained/

For details, refer to the configuration files and scripts in this repository.

## Known Issues

- It OVERWRITES changes you made to your configuration files.
- Too many git aliases.

## Notes

`ports.txt` is generated via `port installed requested and active`.
`myports.txt`, `requested.txt`, and `restore_ports.tcl` are used for MacPorts [migration].

Pull requests are welcome.

[migration]: https://trac.macports.org/wiki/Migration
