[Homebrew] and git will not be installed automatically if absent.
After homebrew and git installed,
execute the following commands to set up a unix machine:

    git clone https://github.com/weakish/dotfiles
    cd dotfiles
    brew bundle install
    cp myconfig.example.py myconfig.py
    # edit myconfig.py
    sh script/setup

[Homebrew]: https://brew.sh/

## Features

- Use homebrew to install packages for macOS and Linux.
- Vim in private mode.
- Neovim and vscode.
- Sign all git commits and tags with ssh key.

## Known Issues

- It OVERWRITES changes you made to your configuration files.
- BSD and Windows are not supported.
- Mercurial `ui.username` is unset.
- Too many git aliases.

## Notes

`Brewfile.lock.json` is updated automatically via `brew bundle install`.
`ports.txt` is generated via `port installed requested and active`.

Pull requests are welcome.
