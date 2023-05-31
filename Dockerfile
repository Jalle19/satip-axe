FROM debian:buster-slim

WORKDIR /build

RUN apt-get -y update && \
  apt-get -y install \
    build-essential \
    python3-minimal \
    git-core \
    wget \
    u-boot-tools \
    bsdmainutils \
    patch \
    fakeroot \
    subversion \
    cpio \
    autoconf \
    libtool \
    shtool \
    pkg-config \
    texinfo \
    gcc-sh4-linux-gnu && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists

#
# Cross-compile and install various dependencies
#
ARG CC=/usr/bin/sh4-linux-gnu-gcc
ARG PREFIX=/usr/sh4-linux-gnu

#
# Build libssl
#
ARG OPENSSL_VERSION=1.1.1u
RUN mkdir openssl && \
  cd openssl && \
  wget -q https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz && \
  tar -xvf openssl-${OPENSSL_VERSION}.tar.gz && \
  cd openssl-${OPENSSL_VERSION} && \
  ./Configure --prefix=${PREFIX} linux-generic32 && \
  make CC=${CC} -j $(nproc) && \
  make install_sw

#
# Build zlib
#
ARG ZLIB_VERSION=1.2.13
RUN mkdir zlib && \
  cd zlib && \
  wget -q https://zlib.net/zlib-${ZLIB_VERSION}.tar.gz && \
  tar -xvf zlib-${ZLIB_VERSION}.tar.gz && \
  cd zlib-${ZLIB_VERSION} && \
  CC=${CC} ./configure --prefix=${PREFIX} && \
  make -j $(nproc) && \
  make install

#
# Build ncurses
#
ARG NCURSES_VERSION=6.4
RUN mkdir ncurses && \
  cd ncurses && \
  wget -q https://ftp.gnu.org/gnu/ncurses/ncurses-${NCURSES_VERSION}.tar.gz && \
  tar -xvf ncurses-${NCURSES_VERSION}.tar.gz && \
  cd ncurses-${NCURSES_VERSION} && \
  CC=${CC} ./configure --host=sh4-linux --prefix=${PREFIX} \
    --without-cxx-binding \
    --without-manpages \
    --disable-stripping && \
  make -j $(nproc) && \
  make install

#
# Build libdvbcsa
#
ARG LIBDVBCSA_COMMIT=bc6c0b164a87ce05e9925785cc6fb3f54c02b026
RUN mkdir libdvbcsa && \
  cd libdvbcsa && \
  git clone https://code.videolan.org/videolan/libdvbcsa.git && \
  cd libdvbcsa && \
  ./bootstrap && \
  CC=${CC} ./configure --host=sh4-linux --prefix=${PREFIX} && \
  make -j $(nproc) && \
  make install

# Required for git operations when container is running as an UID that doesn't exist in /etc/passwd
ENV GIT_COMMITTER_NAME=nobody
ENV GIT_COMMITTER_EMAIL=nobody@example.com

ENTRYPOINT [ "make" ]
