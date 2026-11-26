# Compiling Vim From Source

```sh
# Download packages

$ sudo dnf install gcc make git ncurses-devel python3-devel
```

```sh
# Clone repository

$ git clone https://github.com/vim/vim.git
```

```sh
# Setup/configure

$ cd vim

$ ./configure \
    --prefix $HOME/.local \
    --with-features=huge \
    --enable-python3interp=yes \
    --enable-multibyte \
    --disable-gui \
    --without-x
```

```sh
# Build

$ make -j$(nproc)
$ make install
```

