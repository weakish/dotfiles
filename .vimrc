" private mode
" For more safety, run vim with
"     vim -i None -U None -n --noplugin
" More info:
" https://github.com/zx2c4/password-store/blob/master/contrib/vim/redact_pass.vim
" https://stackoverflow.com/a/15895811/
" https://stackoverflow.com/questions/15895432/how-to-start-vim-in-private-mode#comment103611534_15895811
" https://vi.stackexchange.com/a/1940/

set nobackup
set nowritebackup
set noswapfile
set noshelltemp
set history=0
set viminfo=
set noundofile
set nomodeline
set secure
