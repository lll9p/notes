Raspberry pi 配置
#################
:date: 2016-10-03 09:43
:modified: 2021-03-25 21:41
:status: published
:category: Tech
:tags: raspberry pi, resiliosync, 备份, 配置
:series: Raspberry Pi
:slug: config_raspberry_pi
:authors: lao
:summary: Raspberry Pi 配置

前言
====

Raspberry pi 是一个ARM开发板，我用的是 `Raspberry pi 2 model B`_ 俗称2B版，4核ARM Cortex-A7 CPU（900MHZ），1GB内存。

rpi2B带USB wifi时功耗仅1~5W，很适合用来搭要求不高的家庭长期服务系统，比如本文所述的 `dnspod DDNS自动更新`_ 、 `内网穿透`_ 、 `hostapd配置wifi`_ 、 `ResilioSync同步(原BTSync)`_ 、`aria2 下载服务`_ 等，配置好了就不用再管了，做个小玩具挺好。


系统安装
========

系统我选 Archlinux_ ，毕竟pc和自己的服务器上长期使用 Archlinux ，再加上好用的滚动更新，有什么理由不在 rpi2B 上装个 Archlinux ？

具体安装方法 `Archlinux ARM 安装指引`_ 进行安装，很简单，不赘述。默认用户名 ``alarm`` ，密码同用户名。敢死队长 ``root`` 密码为 ``root`` 。

*系统安装不一定要在linux上，显然可以用VirtualBox里的Linux来安装，* 系统恢复_ *也可以在里面进行恢复。*

系统配置
========

安装完，登录前运行 ``touch boot/ssh`` 并 ``echo hdmi_force_hotplug=1 >> boot/config.txt``

在 `boot/boot.txt` 修改 `root` 为 `ro` ，即只读模式，安装 `uboot-tools` 并执行 ``./mkscr`` 。

同样，在 `etc/fstab` 中也需要将boot分区变为ro ``defaults,ro,errors=remount-ro``

安装树莓派专用内核 pacman -Syyu linux-raspberrypi4 raspberrypi-firmware

修改etc/fstab 为0p1

修改/boot/cmdline.txt 删除 kgdboc=ttyAMA0,115200
修改/boot/config.txt 增加 hdmi_force_hotplug=1 enable_uart=1

初次使用配置
------------

初始账户和密码均为alarm

ssh登录后先 ``su`` 到 `root` ，然后

``vi /etc/ssh/sshd_config``

加入一行: ``PermitRootLogin yes`` ；

重启 `sshd` ``systemctl restart sshd`` ；

从 `sshd_config` 删除 ``PermitRootLogin yes`` ；


修改 `pacman` 镜像 ``vi /etc/pacman.d/mirrorlist`` ：

``Server = http://mirrors.ustc.edu.cn/archlinuxarm/$arch/$repo``

改用户名
---------

按个人习惯，先改掉默认的用户名。
如果你直接用alarm登录，是无法修改用户名的，先用 `root` 登录。

.. code-block:: bash

    new_user=lao
    # change user name
    usermod -l $new_user -d /home/$new_user -m alarm
    # chenge user group
    groupmod -n $new_user alarm

修改用户密码 ``passwd lao`` 。

安装 `sudo`
-----------

先装个 `sudo` ，不能裸奔。

.. code-block:: bash

    pacman -S sudo
    visudo
    # uncomment the line "%wheel ALL=(ALL) ALL"

.. code-block:: bash

    vi /etc/locale.gen
    # uncomment en_US.UTF-8 UTF-8
    locale-gen

时间相关
---------

.. code-block:: bash

    timedatectl set-ntp true
    rm /etc/localtime
    ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

然后就可以重启了，最后要安装 `lrzsz` 和 `tmux` 。

配置bash
---------

从TLDP上的 `.bashrc样例`_ 拿到配置好的 ``.bashrc`` 即可。

.. code-block:: bash

   wget https://gist.github.com/lll9p/a1df902cc68171bb6b3dca31891629c0/raw/4dfdd03af92335f17eec12e0b4b0cd3ce2584eaf/.bash .bashrc

上面的配置很全面了，只需要加上自己的一些，如：

.. code-block:: bash

    # If not running interactively, don't do anything
    [[ $- != *i* ]] && return
    set editing-mode vi
    set -o vi
    export PATH+=:/opt/vc/bin
    export LANG=en_US.UTF-8

启动时检查硬盘
---------------

rpi不自带电池，系统所在的MicroSD卡又容易出现问题，所以每次开机都对硬盘自检是最好了。在 `/boot/cmdline.txt` 中设置系统启动时硬盘只读，进行磁盘检查之后再 `mount` 到 `/` 即可。

#. 在 `/boot/cmdline.txt` 中的 `root=/dev/mmcblk0p2` 后的 `rw` 改为 `ro` 。即：

   .. code-block:: console

       root=/dev/mmcblk0p2 ro rootwait console=ttyAMA0,115200 console=tty1 selinux=0 plymouth.enable=0 smsc95xx.turbo_mode=N dwc_otg.lpm_enable=0 kgdboc=ttyAMA0,115200 elevator=noop

#. 在 `/etc/fstab` 中，加一行：

   .. code-block:: console

        /dev/mmcblk0p2  /       ext4    remount,rw,defaults,noatime        0       1

安装其他“必备软件”
-------------------

.. code-block:: console

    sudo pacman -S --needed bash-completion bzip2 coreutils dhcpcd dkms dnsmasq dosfstools e2fsprogs findutils gawk gcc gcc-libs gzip hostapd less lrzsz p7zip rp-pppoe sudo sysfsutils tmux unzip vim watchdog wireless_tools wiringpi wpa_supplicant alsa-firmware alsa-utils aria2 cblas dkms dnsmasq hdf5 hdparm lapack moc rng-tools samba wget which wqy-zenhei mldonkey


网络配置
========

`ArchlinuxARM`_ 默认设好了 `DHCP` ，不需要额外配置，不过 `wifi` 之类的还是要自己设置的，由于我用的是 `RTL8188EUS` 芯片的USB网卡，自带驱动无法启动 `hostapd` ，所以还是需要进行一番安装与设置。

hostapd配置wifi
----------------

之前为了启用RTL8188EUS网卡（用 ``lsusb`` 命令可以查看），需要下载 `jenssegers RTL8188-hostapd 驱动`_ 然后编译。

别一个好办法是下载 `lwfinger RTL8188 驱动`_ ，然后用dkms管理编译和安装，这样可以直接使用Arch库里的hostapd，不过每次内核更新的时候就要再运行一次 ``sudo dkms install 8188eu/1.0`` 。

.. code-block:: bash

    wget https://github.com/lwfinger/rtl8188eu/archive/v4.1.8_9499.zip
    unzip v4.1.8_9499.zip
    sudo dkms add ./rtl8188eu
    sudo dkms build 8188eu/1.0
    sudo dkms install 8188eu/1.0
    sudo touch \etc\modprobe.d\8188eu.conf
    sudo echo "# r8188eu is staging, 8188eu is off-kernel \n blacklist r8188eu \n options 8188eu rtw_power_mgnt=0 rtw_enusbss=0" > \etc\modprobe.d\8188eu.conf


重启后完成驱动安装，接下来要配置 ``hostapd`` ，可以直接下载 `我的 hostapd 配置`_ ，存为 ``/etc/hostapd/hostapd.conf`` ，修改 ``wpa_passphrase=PasswordOfLao`` 中的密码即完成 ``hostapd`` 的安装与配置。

**以下内容编译自** `Linsir的博客`_ 。

#. dnsmasq
    软AP( ``hostapd`` )设置好后，我们还需要个DHCP服务器为设备分配IP地址。这里我们选用轻量级的dnsmasq,它还可以提示DNS缓存，非常给力。
    ``pacman -S dnsmasq`` 后编辑 ``/etc/dnsmasq.conf`` ，以下是简单的配置，具体的配置及解释请参考 `我的 dnsmasq 配置`_ 。

    .. code-block:: config

       # 无线网卡的设备名，同 hostapd.conf 保持一致
       interface=wlan0
       # 监听地址，同你想设置的网关地址
       listen-address=192.168.0.1
       bind-interfaces
       # DHCP 分配  IP 的起止段和租约时间
       dhcp-range=192.168.0.100,192.168.0.200,12h
       # 推送给客户端的 DNS 服务器
       dhcp-option=6,114.114.114.114,223.5.5.5
       iptables

#. 设置流量转发

   .. code-block:: console

       # 设置
       sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
       # 保存
       sudo iptables-save > /etc/iptables/iptables.rules

#. 允许转发
    需要启用内核的 IPv4 包转发功能，才能正常访问互联网。

    .. code-block:: console

         sudo echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.d/99-sysctl.conf
         sudo sysctl -p /etc/sysctl.d/99-sysctl.conf

#. 测试
    必须先为无线网卡设置好网关和子网掩码，这样 ``hostapd`` 启用后，无线网络才能正确获取到IP地址。

    .. code-block:: console

         sudo ifconfig wlan0 192.168.0.1 netmask 255.255.255.0
         sudo systemctl start iptables
         sudo systemctl start hostapd
         sudo systemctl start dnsmasq

    现在就可以用手机或者笔记本连接，就能获得地址并能上网了。

#. 开机启动
    每次运行 ``hostapd`` 之前，都必须运行命令来初始化无线网卡 ``wlan0``，很麻烦。如果我们要开机就激活无线网络，就要先用自带的 ``netctl`` 来管理，配置 ``/etc/netctl/wireless-wpa-static`` ：

    .. code-block:: config

      Interface=wlan0
      Connection=ethernet
      IP=static
      Address='192.168.0.1/24'
      #Gateway='192.168.0.1'
      SkipNoCarrier=yes
      ExecUpPost='iptables-restore < /etc/iptables/iptables.rules &&echo 1 >/proc/sys/net/ipv4/ip_forward'

    设置开机启动：

    .. code-block:: console

      sudo netctl enable wireless-wpa-static
      sudo systemctl enable iptables hostapd dnsmasq

#. PPPOE
    我的 ``rpi`` 是连路由的，倒不用拨号，若是不用路由，就需要 ``pppoe`` 拨号了。

    .. code-block:: console

      sudo pacman -S rp-pppoe
      sudo pppoe-setup # 设置 拨号帐户、密码等
      sudo systemctl enable adsl

#. iptables
    我们需要再次配置 iptables，让网络流量得以穿透 PPPOE 隧道。

    .. code-block:: console

        sudo iptables -t nat -A POSTROUTING -o ppp0 -j MASQUERADE
        sudo iptables-save > /etc/iptables/iptables.rules

最后重启，一个无线路由器就成功了。Enjoy it.

dnspod DDNS自动更新
-------------------

请参考 `ddns自动更新`_ 。

内网穿透
-------------

有时候公司内网需要在外访问，这时最好用的就是内网穿透工具了，这里推荐 `frp`_ ，`ngrok`_ 也可用 。

frp
....

`frp`_ 是一个开源的网罗穿透工具，下载 `linux_arm` 的release即可。

ngrok
.....

`ngrok`_ 是一个网络穿透的服务， ``ngrok 2`` 是收费服务，而 ``ngrok 1`` 则是开源的，我们可以使用 ``ngrok 1`` 。

``ngrok`` 需要编译，过程如下：

.. code-block:: console

    git clone https://github.com/inconshreveable/ngrok.git ngrok
    cd ngrok
    vim src/ngrok/log/logger.go
    # 第五行import中的 log 包，改为：log "github.com/keepeye/log4go"
    # 为根域名生成证书
    export NGROK_DOMAIN="laolilin.com"
    openssl genrsa -out rootCA.key 2048
    openssl req -x509 -new -nodes -key rootCA.key -subj "/CN=$NGROK_DOMAIN" -days 5000 -out rootCA.pem
    openssl genrsa -out device.key 2048
    openssl req -new -key device.key -subj "/CN=$NGROK_DOMAIN" -out device.csr
    openssl x509 -req -in device.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out device.crt -days 5000
    yes | cp rootCA.pem assets/client/tls/ngrokroot.crt
    yes | cp device.crt assets/server/tls/snakeoil.crt
    yes | cp device.key assets/server/tls/snakeoil.key
    # 指定编译的环境变量: linux
    GOOS=linux GOARCH=amd64
    make release-server release-client
    # Raspberry pi
    GOOS=linux GOARCH=arm
    make release-server release-client
    # windows
    GOOS=windows GOARCH=386
    make release-server release-client

编译完成后在 ``./bin/`` 下找到 ``ngrokd`` 及 ``ngrok`` 。
 ``sudo cp ./bin/arm/{ngrokd,snakeoil.crt,snakeoil.key} /usr/local/sbin/`` ，然后开一个专用的ngrok用户，及专用 ``pid`` 文件。

.. code-block:: bash

   # add ngrok user without home dir and cannot login
   sudo useradd --shell /bin/nologin --no-create-home --user-group ngrok
   # create an empty ngrok directory on /var/run using systemd or ngrok cannot create pid file
   sudo echo 'd /var/run/rslsync 0755 ngrok ngrok' > /usr/lib/tmpfiles.d/ngrok.conf

另存下面的代码为 ``/usr/lib/systemd/system/ngrok-server.service`` ，并启用之： ``sudo systemctl enable ngrok-server``  。

.. code-block:: config
    #filepath:/usr/lib/systemd/system/ngrok-server.service
    [Unit]
    Description=ngrok-server
    After=network.target

    [Service]
    Type=simple
    User=ngrok
    Group=ngrok
    ExecStart=/usr/local/sbin/ngrokd -log-level="ERROR" -tlsKey=/usr/local/sbin/snakeoil.key -tlsCrt=/usr/local/sbin/snakeoil.crt -domain=laolilin.com -httpAddr=:8888 -httpsAddr=:8081
    PIDFile=/var/run/ngrok/ngrokd.pid
    Restart=always

    [Install]
    WantedBy=multi-user.target

把以下内容存为 ``ngrok.conf`` 。

.. code-block:: config

   server_addr: "rpi.laolilin.com:4443"
   trust_host_root_certs: false
   tunnels:
     jupyter:
       remote_port: 8889
       proto:
         tcp: "8889"
     rdp:
       remote_port: 9000
       proto:
         tcp: "3389"

最后，在内网电脑上执行命令： ``ngrok.exe -config=ngrok.conf start jupyter rdp`` （或放入 ``计划任务`` 中），即可在外网访问内网的 ``远程桌面`` 及 ``jupyter notebook`` 。

系统备份与恢复
==============

辛辛苦苦安装并配置好的系统因各种原因（比如 `我删过/`_ ）丢失或损坏，如果此时有一份备份，那是最好不过的了。

系统与配置备份
--------------

在这里我用 ``tar`` 命令来按日备份系统，并排除掉一些动态的系统目录。

当然了有时候并不用备份整个系统，只要备份修改过的配置文件即可，毕竟全系统备份很耗时。

+----------+--------+----------+
| 备份项目 | 全系统 | 仅配置   |
+----------+--------+----------+
| 耗时     | 2.5min | 20second |
+----------+--------+----------+

在 ``.bashrc`` 下加两句 ``alias`` 即可。

.. code-block:: bash

    alias backup_system="sudo tar --exclude=/{dev,lost+found,mnt,proc,run,sys,tmp,var/lib/pacman} --exclude=/home/python/{venv,PyNote,.cache,.viminfo,.theano,.ipython,.local} --exclude=/home/user/{.cache,.vimtmp,moc,.config/cmus} --exclude=/home/git/repos --xattrs -cpzf /mnt/MHDD/system_backup/backup-`date +%Y-%m-%d`.tgz /"
    alias backup_system_config="sudo tar --xattrs -cpzf /mnt/MHDD/system_backup/backup-config-`date +%Y-%m-%d`.tgz \
        /boot/{cmdline.txt,config.txt} \
        /etc/{conf.d/,hostapd/,iptables/,modprobe.d/,modules-load.d/,netctl/{pppoe,wireless-wpa-static},pacman.d/mirrorlist,ppp/{ip-up.d/01-dynamicIP.sh,chap-secrets,pap-secrets,pppoe.conf},rslsync/,ssh/,systemd/user/aria2.service,sysctl.d/,samba/,wpa_supplicant/,dhcpcd.conf,dhcpcd.duid,dnsmasq.conf,fstab,group,group-,gshadow,gshadow-,hostname,locale.gen,pacman.conf,passwd,passwd-,resolv.conf,shadow,shadow-,sudoers,watchdog.conf} \
        /home/{user/{.config/aria2,.ssh,.vim,.bashrc,.toprc,.vimrc},git/{.ssh,.bashrc},python/{.config/matplotlib/,.jupyter/,.bashrc}} \
        /root/{.gnupg/,.bashrc} \
        /usr/{lib/{systemd/system/{hdparm.service,rslsync.service,ddns-update.service,ddns-update.timer,dnsmasq.service,hostapd.service,jupyter-notebook.service,ngrok-server.service,watchdog.service},tmpfiles.d/{rslsync.conf,jupyter.conf,ngrok.conf}},local/sbin/{ddns_dnspod.py,forward-ssh.sh,ngrokd,snakeoil.crt,snakeoil.key,start-jupyter-notebook}}"

系统恢复
--------

解压很简单，只要一行即可，需要注意的是，若要还原整个系统，需要把 ``/boot`` mount进“根目录里”。

.. code-block:: bash

   mkdir boot root
   sudo mount /dev/sdx1 root
   sudo mount /dev/sdx2 root/boot
   tar xvpfz backup.tgz -C root

ResilioSync同步(原BTSync)
=========================

ResilioSync_ （以下简称rslsync），也就是改名前的BTSync，基于BitTorrent协议的文件分享系统。可以用pi+rslsync来做同步服务器，我把PC上的Dropbox文件夹放rslsync中同步，实现双重备份，经一年多的使用，挺稳定的。

下载resiliosync并解压
----------------------

在Pi上插一个1.5T的移动硬盘，以下步骤可使用它来做Resiliosync的硬盘。

.. code-block:: bash

   # download & extract Resiliosync
   wget https://download-cdn.resilio.com/stable/linux-armhf/resilio-sync_armhf.tar.gz
   tar xvzf resilio-sync_armhf.tar.gz
   sudo mv rslsync /usr/local/sbin
   # mount the mobile hard disk drive
   # replace sdx with your real device name
   sudo mount /dev/sdx /mnt/MHDD

创建rslsync用户及相关配置
-------------------------

开一个专用的rslsync用户对于系统控制很有好处，可以将rslsync与其他用户隔离开来，下面的代码将创建一个 **无家目录** 且 **不能登录** 的 ``rslsync`` 用户。

.. code-block:: bash

   # add rslsync user without home dir and cannot login
   sudo useradd --shell /bin/nologin --no-create-home --user-group rslsync
   # create an empty rslsync directory on /var/run using systemd or rslsync cannot create pid file
   echo 'd /var/run/rslsync 0755 rslsync rslsync' | sudo tee /usr/lib/tmpfiles.d/rslsync.conf
   # make config file path and dump sample config to it
   sudo mkdir /etc/rslsync/
   rslsync --dump-sample-config | sudo tee /etc/rslsync/config.json

编辑 ``config.json`` ,把 ``"storage_path"`` 设成 ``"/mnt/MHDD/.sync"`` ，``"pid_file"`` 设为 ``"/var/run/rslsync/rslsync.pid"`` 。
开机启动rslsync，编辑 ``/usr/lib/systemd/system/rslsync.service`` ，为方便其他用户能读写同步的文件，需要对rslsync的umask进行设置 ``0002`` 。

.. code-block:: bash

    [Unit]
    Description=Resilio Sync
    After=mnt-MHDD.mount
    After=systemd-fsck@.service

    [Service]
    Type=forking
    User=rslsync
    Group=rslsync
    UMask=0002
    PIDFile=/var/run/rslsync/rslsync.pid
    ExecStart=/usr/local/sbin/rslsync --config /etc/rslsync/config.json
    Restart=on-abort

    [Install]
    WantedBy=multi-user.target

然后 ``sudo systemctl enable rslsync`` 即可。

aria2 下载服务
===============

#. 安装 ``aria2`` ：
   直接从 ``pacman`` 安装即可，顺手创建配置文件。

   .. code-block:: console

        sudo pacman -S aria2
        mkdir -p .config/aria2 && cd $_
        touch session.lock aria2.conf

   编辑 ``aria2.conf`` ，输入以下配置，注意把 `MYSECRET` 改成自己的token，以后在 `百度网盘导出`_ 及 `迅雷离线导出`_ 里，设置jsonrpc为 `http://token:MYSECRET@aria2server.com:6800/jsonrpc`` 即可顺利使用。

   .. code-block:: config

       # 基本配置
       # 下载目录
       dir=/mnt/DISKOFLAO/Downloads
       # 下载从这个文件中找到的urls, 需自己建立这个文件
       # touch /home/pi/.aria2/aria2.session
       input-file=/home/lao/.config/aria2/session.lock
       # 最大同时下载任务数，默认 5
       #max-concurrent-downloads=5
       # 断点续传，只适用于 HTTP(S)/FTP
       continue=true
       log-level=error
       # HTTP/FTP 配置
       # 关闭连接如果下载速度等于或低于这个值，默认 0
       #lowest-speed-limit=0
       # 对于每个下载在同一个服务器上的连接数，默认 1
       max-connection-per-server=5
       # 每个文件最小分片大小，例如文件 20M，设置 size 为 10M, 则用2个连接下载，默认 20M
       #min-split-size=10M
       # 下载一个文件的连接数，默认 5
       #split=5
       # BT 特殊配置
       # 启用本地节点查找，默认 false
       bt-enable-lpd=true
       # 指定最大文件数对于每个 bt 下载，默认 100
       #bt-max-open-files=100
       # 单种子最大连接数，默认 55
       #bt-max-peers=55
       # 设置最低的加密级别，可选全连接加密 arc4，默认是头加密 plain
       #bt-min-crypto-level=plain
       # 总是使用 obfuscation handshake，防迅雷必备，默认 false
       bt-require-crypto=true
       # 如果下载的是种子文件则自动解析并下载，默认 true
       #follow-torrent=true
       # 为 BT 下载设置 TCP 端口号，确保开放这些端口，默认 6881-6999
       listen-port=65298
       #Set UDP listening port used by DHT(IPv4, IPv6) and UDP tracker
       dht-listen-port=65298
       # 整体上传速度限制，0 表示不限制，默认 0
       #max-overall-upload-limit=0
       # 每个下载上传速度限制，默认 0
       #max-upload-limit=0
       # 种子分享率大于1, 则停止做种，默认 1.0
       #seed-ratio=1
       # 做种时间大于2小时，则停止做种
       seed-time=120
       # RPC 配置
       # 开启 JSON-RPC/XML-RPC 服务，默认 false
       enable-rpc=true
       # 允许所有来源，web 界面跨域权限需要，默认 false
       rpc-allow-origin-all=true
       # 允许外部访问，默认 false
       rpc-listen-all=true
       # rpc 端口，默认 6800
       rpc-listen-port=6800
       # 设置最大的 JSON-RPC/XML-RPC 请求大小，默认 2M
       #rpc-max-request-size=2M
       # rpc 密码，可不设置
       #rpc-passwd=raspberry
       # 做种时间大于2小时，则停止做种
       seed-time=120
       # RPC 配置
       # 开启 JSON-RPC/XML-RPC 服务，默认 false
       enable-rpc=true
       # 允许所有来源，web 界面跨域权限需要，默认 false
       rpc-allow-origin-all=true
       # 允许外部访问，默认 false
       rpc-listen-all=true
       # rpc 端口，默认 6800rpc-listen-port=6800
       # 设置最大的 JSON-RPC/XML-RPC 请求大小，默认 2M
       #rpc-max-request-size=2M
       # rpc 密码，可不设置
       #rpc-passwd=raspberry
       # rpc 用户名，可不设置
       #rpc-user=aria2pi
       rpc-secret=MYSECRET
       # 高级配置
       # This is useful if you have to use broken DNS and
       # want to avoid terribly slow AAAA record lookup.
       # 默认 false
       disable-ipv6=true
       # 指定文件分配方法，预分配能有效降低文件碎片，提高磁盘性能，缺点是预分配时间稍长
       # 如果使用新的文件系统，例如 ext4 (with extents support), btrfs, xfs or NTFS(MinGW build only), falloc 是最好的选择
       # 如果设置为 none，那么不预先分配文件空间，默认 prealloc
       file-allocation=prealloc
       # 整体下载速度限制，默认 0
       #max-overall-download-limit=0
       # 每个下载下载速度限制，默认 0
       #max-download-limit=0
       # 保存错误或者未完成的下载到这个文件
       # 和基本配置中的 input-file 一起使用，那么重启后仍可继续下载
       save-session=/home/lao/.config/aria2/session.lock
       # 每5分钟自动保存错误或未完成的下载，如果为 0, 只有 aria2 正常退出才回保存，默认 0
       save-session-interval=300
       # 若要用于 PT 下载，需另外的配置，这里没写

#. 开机启动
    ``aria2`` 开机启动很简单，把以下代码存为 ``/etc/systemd/user/aria2.service`` ，然后 ``systemctl enable aria2.service --user`` ，即可。

   .. code-block:: config

       [Unit]
       Description=Aria2 Service
       After=mnt-MHDD.mount
       After=systemd-fsck@.service
       After=network.target

       [Service]
       Type=simple
       User=lao
       Group=lao
       UMask=0002
       PIDFile=/home/lao/.config/aria2/aria2.pid
       ExecStart=/usr/bin/aria2c --check-certificate=false --enable-rpc=true --rpc-listen-all=true --rpc-allow-origin-all=true --rpc-secret=passwd --save-session /home/lao/.config/aria2/session.lock --input-file /home/lao/.config/aria2/session.lock --conf-path=/home/lao/.config/aria2/aria2.conf
       Restart=on-abort

       [Install]
       WantedBy=multi-user.target

mldonkey 安装

samba 安装
smbpasswd -a lao

.. _Archlinux: https://www.archlinux.org
.. _`Archlinux ARM 安装指引`: https://archlinuxarm.org/platforms/armv7/broadcom/raspberry-pi-2
.. _`Raspberry pi 2 model B`: https://www.raspberrypi.org/products/raspberry-pi-2-model-b/
.. _`.bashrc样例`: http://www.tldp.org/LDP/abs/html/sample-bashrc.html
.. _`我删过/`: https://www.v2ex.com/t/309375
.. _`ArchlinuxARM`: https://archlinuxarm.org/
.. _`jenssegers RTL8188-hostapd 驱动`: https://github.com/jenssegers/RTL8188-hostapd
.. _`lwfinger RTL8188 驱动`: https://github.com/lwfinger/rtl8188eu/tree/v4.1.8_9499
.. _`我的 hostapd 配置`: https://gist.github.com/lll9p/907acbb39c1f4a08f2e0b5aa7a80bede
.. _`我的 dnsmasq 配置`: https://gist.github.com/lll9p/2cdf7e27a663fd5c615d6fc49ca511a8
.. _`ddns自动更新`: //blog.laolilin.com/posts/2016/10/dnspod_ddns_auto_update.html
.. _`Linsir的博客`: https://linsir.org/post/Raspberry_Pi_Wifi_Router
.. _ResilioSync: https://www.resilio.com/
.. _`ngrok`: http://www.ngrok.com
.. _`frp`: https://github.com/fatedier/frp
.. _`百度网盘导出`: https://github.com/acgotaku/BaiduExporter
.. _`迅雷离线导出`: https://github.com/binux/ThunderLixianExporter
