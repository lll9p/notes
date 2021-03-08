dnspod DDNS 自动更新
####################
:date: 2016-10-15 12:05
:modified: 2016-10-28 17:01
:status: published
:category: Tech
:tags: dnspod, DDNS
:series: Raspberry Pi
:slug: dnspod_ddns_auto_update
:authors: lao
:summary: 使用Python对dnspod进行DDNS更新
:toc: show

前言
====

由于把 ``blog`` 托管在 ``github pages`` 和 ``coding pages`` ，再加上 `我的Raspberry pi`_ 也需要暴露于网络中，所以最好能及时更新域名的IP。

利用 `DNSPOD`_ 的 ``DDNS API`` ，我们可以轻松在 ``Raspberry Pi`` 上实现这个需求。

代码实现
========

利用 `DNSPOD`_ 的 ``API`` ，很容易写出自动更新的代码，需要注意的一点是， ``API`` 不允许一小时五次都更新同一 ``IP`` ，所以代码里考虑到这点，对比二者，如果相同则不进行操作。

``login_token`` 可以从 `DNSPOD`_ 获取，按格式把域名和ip填入 ``data`` 。

保存如下代码为 ``/usr/local/sbin/ddns_update.py`` 。

.. code-block:: python

    #!/usr/bin/python
    # Author: lao
    # url: http://laolilin.com
    import socket
    import urllib.parse
    import urllib.request
    import json


    def initReq(url, values):
        '''
        simple request data from url with values
        '''
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data)
        try:
            res = urllib.request.urlopen(req)
        except:
            raise
        return res


    def getIp():
        '''
        grab the ip of the machine
        '''
        data = initReq('http://ip.taobao.com/service/getIpInfo2.php',{'ip':'myip'})
        return json.loads(data.read().decode())['data']['ip']


    def updateData():
        '''
        update ip records of data, prepared for update it
        '''
        res = initReq(url=DomainListUrl, values=loginInfo)
        domainIDs = {i['name']: i['id']
                     for i in json.loads(res.read().decode())['domains']}
        for domain in data:
            domain['domainID'] = domainIDs.get(domain['domain'])
            res = initReq(url=RecordListUrl, values={
                **loginInfo, **{'domain_id': domain['domainID']}})
            subdomainInfo = {((i['name'], i['line']) if i['type'] == 'A' else ('invalid', 'invalid')):
                             {'IP': i['value'], 'ID': i['id']}
                             for i in json.loads(res.read().decode())['records']}
            subdomains = domain['subdomains']
            for name in subdomains:
                subdomains[name].update(subdomainInfo.get(name))
                ipList = socket.gethostbyname_ex(subdomains[name]['hostname'])
                subdomains[name]['hostIP'] = ipList[-1][-1]


    def main():
        updateData()
        httpData = []
        for domain in data:
            subdomains = domain['subdomains']
            for subdomain, _ in subdomains.items():
                # avoid update too frequenly
                if _['IP'] != _['hostIP']:
                    httpData.append(
                        {
                            **loginInfo,
                            **{
                                'domain_id': domain['domainID'],
                                'record_id': _['ID'],
                                'record_line': subdomain[1],
                                'sub_domain': subdomain[0],
                                'value': _['hostIP']
                            }
                        }
                    )
                else:
                    continue
        for item in httpData:
            try:
                initReq(url=RecordDdnsUrl, values=item)
            except:
                pass

    DomainListUrl = 'https://dnsapi.cn/Domain.List'
    RecordListUrl = 'https://dnsapi.cn/Record.List'
    RecordDdnsUrl = 'https://dnsapi.cn/Record.Ddns'
    loginInfo = {
        'login_token': '**your login token**',
        'format': 'json'
    }
    data = [
            {'domain': 'laolilin.com',
             'domainID': '',
             'subdomains': {('blog', '默认'): {'ID': '',
                                          'IP': '',
                                          'hostIP': '',
                                          'hostname': 'pages.coding.me'},
                            ('blog', '国外'): {'ID': '',
                                          'IP': '',
                                          'hostIP': '',
                                          'hostname': '192.30.252.153'},
                            ('pi', '默认'): {'ID': '',
                                          'IP': '',
                                          'hostIP': '',
                                          'hostname': getIp()},
                            }
             },
            ]


    if __name__ == "__main__":
        main()

自动更新
===========

由于 ``systemd`` 可以轻松实现自动运行脚本，故只需要一个 ``timer`` 和一个 ``service`` 。

#. 创建 ``service``
   ``sudo touch /usr/lib/systemd/system/ddns-update.service`` 先建立个空文件。
   再填入以下内容，意思是用 ``root`` 运行 ``ddns_update.py`` 。

   .. code-block:: systemd

       [Unit]
       Description=Update ip records
       After=network.target

       [Service]
       Type=simple
       ExecStart=python /usr/local/sbin/ddns_update.py
       User=root
       Group=systemd-journal

#. 创建 ``timer``
   ``timer`` 就是个定时器，和 ``ddns_update.service`` 同名, ``sudo touch /usr/lib/systemd/system/ddns-update.timer`` 。
   再填入以下内容，启动后10秒开始执行，每30分钟运行一次。

   .. code-block:: systemd

       [Unit]
       Description=Update ip records.

       [Timer]
       OnBootSec=0.1min
       OnUnitActiveSec=30min
       Unit=ddns-update.service

       [Install]
       WantedBy=timers.target

#. 启用
   很简单，用 ``sudo systemctl enable ddns-update.timer`` 即可。

.. _`我的Raspberry pi`: {filename}/Tech/computer.Rpi.2016.10.raspberry_pi_配置.rst
.. _`DNSPOD`: //www.dnspod.cn
