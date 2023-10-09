Ensure that git is installed, then:

    git clone https://github.com/weakish/dotfiles
    cd dotfiles
    cp myconfig.example.py myconfig.py
    # edit myconfig.py
    sh script/setup

## Features

- Vim in private mode.
- Sign all git commits and tags with ssh key.

## Known Issues

- It OVERWRITES changes you made to your configuration files.
- BSD and Windows are not supported.
- Too many git aliases.

## Notes

`Brewfile.lock.json` is updated automatically via `brew bundle install`.
`ports.txt` is generated via `port installed requested and active`.
`myports.txt`, `requested.txt`, and `restore_ports.tcl` are used for MacPorts [migration].

Pull requests are welcome.

[migration]: https://trac.macports.org/wiki/Migration
