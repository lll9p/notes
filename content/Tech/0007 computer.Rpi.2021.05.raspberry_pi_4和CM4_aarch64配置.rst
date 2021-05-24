Raspberry pi 配置
#################
:date: 2021-05-24 16:05
:modified: 2021-05-24 16:05
:status: published
:category: Tech
:tags: raspberry pi, compute module, cm4, 配置
:series: Raspberry Pi, cm4
:slug: config_raspberry_pi4_and_cm4_aarch64
:authors: lao
:summary: Raspberry Pi 4 和 CM4 aarch64 配置

前言
====

Raspberry Pi 4 和 Raspberry Pi Compute Module(CM4) 具备BCM2711 1.5GHz 4 核心 64-bit ARM Cortex-A72 CPU，Rpi4我用的是8GB内存，CM4是8GB无线+32GB EMMC的版本。

64位系统的安装比较麻烦，此处特记录。

系统安装
========

系统我选 Archlinux_ ，与之前的树莓派一致。

具体安装方法 `Archlinux ARM 安装指引`_ 进行安装，很简单，不赘述。默认用户名 ``alarm`` ，密码同用户名。敢死队长 ``root`` 密码为 ``root`` 。


运行前配置
==========

** 以下不注明的都是在 `Raspberry Pi 4` 上进行操作 **

安装TF卡前，根据 `Archlinux ARM 安装指引_` 首次安装后要执行 `sed -i 's/mmcblk0/mmcblk1/g' root/etc/fstab` 替换启动盘。

`Raspberry Pi 4` 有时候在不插HDMI的时候无法启动，为防止不能启动，HDMI配置为热插拔： ``echo hdmi_force_hotplug=1 >> boot/config.txt``

开启串口： ``echo enable_uart=1 >> boot/config.txt``

安装TF卡，启动、插上网线并使用串口登录 `root`

修改软件源
-----------
`/etc/pacman.d/mirrorlist` 加入

`Server = https://mirrors.ustc.edu.cn/archlinuxarm/$arch/$repo`

替换`Raspberry Pi 4`专用内核
----------------------------

默认的内核是 `linux-aarch64` ，目前无法在 `CM4` 上顺利启动，我们需要替换为 *专用内核* 。

.. code-block:: bash

   pacman -Syyu linux-raspberrypi4 raspberrypi-firmware

安装完毕后将 `/etc/fstab` 为 `/dev/mmcblk0p1` 。

**暂不重启**

启动设置
---------

#. 开启 `ssh`

``touch /boot/ssh``

#. 其他启动设置

为防止不能启动，修改 `/boot/cmdline.txt` 删除 `kgdboc=ttyAMA0,115200`
在 `/boot/cmdline.txt` 修改 `rw` 为 `ro` ，即只读模式 。
同样，在 `/etc/fstab` 中也需要将boot分区变为ro ``defaults,ro,errors=remount-ro``

**重启进入系统，以 `root` 登录**

无线设置
------------

目前系统默认找不到无线网卡，需要运行 ``rmmod brcmfmac && modprobe brcmfmac`` 加载无线网卡驱动。

**对于 `CM4`**

需要将驱动改名：

.. code-block:: bash

   cd /lib/firmware/brcm
   cp 'brcmfmac43455-sdio.Raspberry Pi Foundation-Raspberry Pi Compute Module 4.txt' 'brcmfmac43455-sdio.raspberrypi,4-compute-module.txt'
   rmmod brcmfmac && modprobe brcmfmac


其他设置
---------

#. 安装一些基本软件

   ``pacman -S sudo tmux ufw``

#. 启用 `sshd` ``systemctl enable sshd`` ；

#. 修改用户名

按个人习惯，先改掉默认的用户名。
如果你直接用alarm登录，是无法修改用户名的，先用 `root` 登录。

.. code-block:: bash

    new_user=YOURNAME
    # change user name
    usermod -l $new_user -d /home/$new_user -m alarm
    # chenge user group
    groupmod -n $new_user alarm

修改用户密码 ``passwd $new_user`` 。

#. `sudo` 配置

.. code-block:: bash

    visudo
    # uncomment the line "%wheel ALL=(ALL) ALL"

.. code-block:: bash

    vi /etc/locale.gen
    # uncomment en_US.UTF-8 UTF-8
    locale-gen

#. 时间设置

.. code-block:: bash

    timedatectl set-ntp true
    rm /etc/localtime
    ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

**配置完成，现在可以重启并 `ssh` 进入系统了**

.. _Archlinux: https://www.archlinux.org
.. _`Archlinux ARM 安装指引`: https://archlinuxarm.org/platforms/armv8/broadcom/raspberry-pi-4
.. _`ArchlinuxARM`: https://archlinuxarm.org/
