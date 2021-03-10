用 Docker 编译 Openwrt
######################
:date: 2020-02-11 17:57
:modified: 2020-02-11 17:57
:status: published
:category: Tech
:tags: Docker, Openwrt
:series: Openwrt
:slug: using_docker_to_build_openwrt
:authors: lao
:summary: docker编译Openwrt教程

前言
====

家里的 ``斐讯 K2P`` 路由器已经使用了3年了，一直用别人的固件，后来想自己编译固件。

我打算编译和使用 `Lean's OpenWrt`_ ，Lean 的这个固件非常完善，对 ``K2P`` 的无线支持的非常好（开源的 `Openwrt`_ ``K2P`` 的无线没办法 ``2.4G`` 和 ``5G`` 同时使用）。

采用 `Docker`_ 进行编译有很多好处，避免在宿主机上安装杂七杂八的软件。网上有许多 ``lede-builder`` ，我尝试过使用 `hanxi的lede-docker-builder`_ ，用了几天，发现有一些问题：

#. `Docker`_ 底包用的是 `Ubuntu`_ ``18.04`` ，里面的包都比较老了，尤其是 `Openwrt`_ ``19.07`` 发布之后，有些需要 `Python`_ ``3.5`` 以上版本的包都没办法编译；

#. 镜像文件比较大，解压之后足足有 ``1.82G`` 下载下来非常慢。

折腾了一天，我终于把设置和流程弄好了。

建立 ``Docker`` 镜像
====================

我在 ``github`` 上新建了一个仓库 `lll9p/docker-lede-builder`_ ，要点主要有：

#. 使用 `debian:buster-slim`_ 容器，比较新，而且比完整的 `debian:buster`_ 有所精简；

#. 预安装 `proxychains4`_ 和 `sudo`_ ``proxychains`` 当处于网络环境不好的时候使用代理进行文件下载或提高网速； ``sudo`` 可以进行一些 ``root`` 用户操作；

#. 使用 ``apt-get --no-install-recommends`` 命令进行安装，大幅精简镜像体积；

#. 新建 ``build`` 用户，免于直接使用 ``root`` 编译。

`Dockerfile`_ 如下：

    .. code-block:: dockerfile

        FROM debian:buster-slim
        MAINTAINER lll9p <lll9p.china@gmail.com>

        ARG DEBIAN_FRONTEND=noninteractive

        RUN apt-get update  \
            && apt-get install -y locales curl wget \
            && apt-get install -y --no-install-recommends build-essential \
            asciidoc binutils bzip2 gawk gettext git libncurses5-dev \
            libz-dev patch python3 unzip zlib1g-dev lib32gcc1 \
            libc6-dev-i386 subversion flex uglifyjs git-core \
            gcc-multilib p7zip p7zip-full msmtp libssl-dev texinfo \
            libglib2.0-dev xmlto qemu-utils upx libelf-dev autoconf \
            automake libtool autopoint device-tree-compiler \
            proxychains4 sudo vim \
            && groupadd -r build && useradd -r -u 1000 -g build build \
            && passwd -d root \
            && passwd -d build \
            && echo '%build ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
            && apt-get clean \
            && rm -rf /var/lib/apt/lists/* \
            && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

        ENV LANG en_US.utf8

        USER build
        WORKDIR /home/build

        ENV FORCE_UNSAFE_CONFIGURE=1

        CMD ["/bin/bash"]

``push`` 到 ``github`` 上之后，再在 `Docker`_ 上新建一个 ``repo`` : `lll9p/docker-lede-builder@dockerhub`_ ，在 ``Build configurations`` 那里设置好指向就自动进行 ``build`` 了，经过几次修改提交之后，最后一个 ``build`` 用了11min的样子。``pull`` 镜像下来，大小也才 ``650MB`` ，精简的不错。

一些编译辅助脚本
================

利用脚本可以方便地编译或实现自动化：

#. 目录结构初始化
   - 将 ``/home/\`whoami\`/data/docker`` 挂载到 ``docker`` 的启动目录 ``/home/build`` 。

   - ``data/docker`` 目录下 ``git clone`` `Lean's OpenWrt`_ 。

   - 由于我使用了 `server酱`_ ，顺便也 ``git`` 一份到 ``docker`` 下。

#. 脚本:

   * ``comple.sh``

    该脚本作用是

    #. 进行 ``proxychans`` 设置（需要提前在宿主机上开启代理）
    #. 更新 `lede <//github.com/coolsnowwolf/lede>`_ 和 `server酱 <//github.com/tty228/luci-app-serverchan>`_
    #. 更新 ``feeds``
    #. 由于在之前使用 ``data/docker/lede/scripts/diffconfig.sh > data/diffconfig`` 所以可以用它来更新 ``.config`` ，不必每次都 ``make menuconfig`` 了
    #. 最后是 ``download`` 和 ``make`` 编译，采用 ``5`` 个进程
    #. 如果不希望使用代理进行下载，可以将 ``PROXYCHAINS`` 注释掉

    .. code-block:: bash

         #!/bin/bash
         BUILD_PATH="/home/build"
         PROXYCHAINS="proxychains4 -q "
         echo 'Start build script.'
         echo ''
         echo '--- Modify proxychains configs. ---'
         sudo sed -i '$ d' /etc/proxychains4.conf
         sudo sed -i '$ d' /etc/proxychains4.conf
         echo 'socks5 172.17.0.1 1081' | sudo tee -a /etc/proxychains4.conf
         echo '' | sudo tee -a /etc/proxychains4.conf

         echo '--- Pull from git server. ---'
         echo ''
         echo '--- Pull from lede. ---'
         cd ${BUILD_PATH}/lede
         ${PROXYCHAINS} git pull
         echo '--- Pull from luci-app-serverchan. ---'
         cd ${BUILD_PATH}/luci-app-serverchan
         ${PROXYCHAINS} git pull
         echo ''
         echo '--- Add luci-app-serverchan to package. ---'
         echo ''
         cd ${BUILD_PATH}/lede
         rm ${BUILD_PATH}/lede/package/feeds/luci/luci-app-serverchan
         ln -s ${BUILD_PATH}/luci-app-serverchan ${BUILD_PATH}/lede/package/feeds/luci/luci-app-serverchan
         ${PROXYCHAINS} ${BUILD_PATH}/lede/scripts/feeds update -a && ${BUILD_PATH}/lede/scripts/feeds install -a

         echo '--- Remove tmp files. ---'
         rm -rf ${BUILD_PATH}/lede/tmp

         echo '--- Remove tmp old config. ---'
         rm -rf ${BUILD_PATH}/lede/.config

         echo '--- Using diff config file. ---'
         cp ${BUILD_PATH}/diffconfig ${BUILD_PATH}/lede/.config

         echo '--- Expand to full config file. ---'
         make defconfig

         echo '--- Download needed files. ---'
         ${PROXYCHAINS} make download

         echo '--- Start build. ---'
         make -j5 V=s

   * ``flash.sh``

    用于自动更新编译好的固件，具体目录和 ``Openwrt`` 的密码请自行更换，依赖 ``sshpass`` 。

    .. code-block:: bash

        #! /bin/bash
        sshpass -p 我的密码 ssh root@192.168.1.1 'rm /tmp/update.bin'
        sshpass -p 我的密码 scp /home/u/data/docker/lede/bin/targets/ramips/mt7621/openwrt-ramips-mt7621-phicomm_k2p-squashfs-sysupgrade.bin root@192.168.1.1:/tmp/update.bin
        sshpass -p 我的密码 ssh root@192.168.1.1 'sysupgrade -v /tmp/update.bin'

使用方法
========

启动 ``docker``
---------------

#. 先使用 ``sudo systemctl start docker`` 启动 ``docker daemon`` ，然后将 `lede <//github.com/coolsnowwolf/lede>`_ 克隆到 data/docker 目录下；

#. 再执行 ``sudo docker pull lll9p/docker-lede-builder`` 安装所需镜像；

#. 执行 ``sudo docker run --rm -it -v /home/u/data/docker:/home/build lll9p/docker-lede-builder`` 即可进入编译环境，可以进行手动编译或者使用之前提供的 ``compile.sh`` 脚本进行自动编译；

#. 可以使用 ``sudo docker run --rm=true -v /home/lao/data/docker:/home/build lll9p/docker-lede-builder /bin/bash /home/build/compile.sh`` 进行自动编译。

.. _`Lean's OpenWrt`: //github.com/coolsnowwolf/lede
.. _`Openwrt`: //openwrt.org
.. _`Docker`: //docker.com
.. _`hanxi的lede-docker-builder`: //github.com/hanxi/lede-docker-builder
.. _`Ubuntu`: //hub.docker.com/_/ubuntu
.. _`Python`: //python.org
.. _`lll9p/docker-lede-builder`: //github.com/lll9p/docker-lede-builder
.. _`debian:buster-slim`: //hub.docker.com/_/debian
.. _`debian:buster`: //hub.docker.com/_/debian
.. _`proxychains4`: //github.com/rofl0r/proxychains-ng
.. _`sudo`: //www.sudo.ws/
.. _`Dockerfile`: //github.com/lll9p/docker-lede-builder/blob/master/Dockerfile
.. _`lll9p/docker-lede-builder@dockerhub`: //hub.docker.com/r/lll9p/docker-lede-builder
.. _`server酱`: //github.com/tty228/luci-app-serverchan
