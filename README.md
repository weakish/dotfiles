[Homebrew] and git will not be installed automatically if absent.
After homebrew and git installed,
execute the following command to set up a unix machine:

    git clone https://github.com/weakish/dotfiles
    cd dotfiles
    brew bundle install
    sh scripts/setup

[Homebrew]: https://brew.sh/

## Features

- Use homebrew to install packages for macOS and Linux.
- Vim in private mode.
- Neovim and vscode.

## Known Issues

- BSD and Windows are not supported.
- Mercurial `ui.username` is unset.

Pull requests are welcome.
