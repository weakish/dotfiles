" private mode
"
" For more safety, ensure there is no vim plugin installed.
" An empty ~/.vim/ directory is recommended.
" More info:
" https://github.com/zx2c4/password-store/blob/master/contrib/vim/redact_pass.vim
" https://stackoverflow.com/a/15895811/
" https://stackoverflow.com/questions/15895432/how-to-start-vim-in-private-mode#comment103611534_15895811
" https://vi.stackexchange.com/a/1940/

set nobackup
set nowritebackup
set noswapfile
set updatecount=0
set noshelltemp
set history=0
set viminfo=
set noundofile
set nomodeline
set secure
