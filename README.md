My dotfiles for macOS.

## Usage

Ensure that git is installed, then:

    git clone https://github.com/weakish/dotfiles
    cd dotfiles
    cp myconfig.example.py myconfig.py
    # edit myconfig.py
    sh script/setup

## Features

- Vim in private mode.

- Sign all git commits and tags with ssh key.

    Git supports signing commits with a GPG, SSH, or X.509 key.
    I prefer the SSH key for signing because I mainly use ssh protocol to communite with git server, thus the ssh key is always available on the machine.

    Please edit `.config/git/allowed_signers` to add your trusted ssh public keys.

## Known Issues

- It OVERWRITES changes you made to your configuration files.
- Too many git aliases.

## Notes

`Brewfile.lock.json` is updated automatically via `brew bundle install`.
`ports.txt` is generated via `port installed requested and active`.
`myports.txt`, `requested.txt`, and `restore_ports.tcl` are used for MacPorts [migration].

Pull requests are welcome.

[migration]: https://trac.macports.org/wiki/Migration
