#!/usr/bin/env python
"""
This module is designed to fetch your external IP address from the internet.
It is used mostly when behind a NAT.
It picks your IP randomly from a serverlist to minimize request
overhead on a single server

If you want to add or remove your server from the list contact me on github


API Usage
=========

    >>> import ipgetter
    >>> myip = ipgetter.myip()
    >>> myip
    '8.8.8.8'

    >>> ipgetter.IPgetter().test()

    Number of servers: 47
    IP's :
    8.8.8.8 = 47 ocurrencies


Copyright 2014 phoemur@gmail.com
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.
"""

import re
import random
import ssl

from sys import version_info

PY3K = version_info >= (3, 0)

if PY3K:
    import urllib.request as urllib
    import http.cookiejar as cjar
else:
    import urllib2 as urllib
    import cookielib as cjar

__version__ = "0.7"


def myip():
    return IPgetter().get_externalip()


class IPgetter(object):

    '''
    This class is designed to fetch your external IP address from the internet.
    It is used mostly when behind a NAT.
    It picks your IP randomly from a serverlist to minimize request overhead
    on a single server
    '''

    def __init__(self):
        self.server_list = ['http://ip.dnsexit.com',
                            'http://ifconfig.me/ip',
                            'http://ipecho.net/plain',
                            'http://checkip.dyndns.org/plain',
                            'http://websiteipaddress.com/WhatIsMyIp',
                            'http://getmyipaddress.org/',
                            'http://www.my-ip-address.net/',
                            'http://myexternalip.com/raw',
                            'http://www.canyouseeme.org/',
                            'http://www.trackip.net/',
                            'http://icanhazip.com/',
                            'http://www.iplocation.net/',
                            'http://www.ipchicken.com/',
                            'http://whatsmyip.net/',
                            'http://www.ip-adress.com/',
                            'http://checkmyip.com/',
                            'http://www.tracemyip.org/',
                            'http://www.lawrencegoetz.com/programs/ipinfo/',
                            'http://www.findmyip.co/',
                            'http://ip-lookup.net/',
                            'http://www.mon-ip.com/en/my-ip/',
                            'http://ipgoat.com/',
                            'http://www.myipnumber.com/my-ip-address.asp',
                            'http://formyip.com/',
                            'https://check.torproject.org/',
                            'http://www.displaymyip.com/',
                            'http://www.bobborst.com/tools/whatsmyip/',
                            'http://www.geoiptool.com/',
                            'https://www.whatsmydns.net/whats-my-ip-address.html',
                            'https://www.privateinternetaccess.com/pages/whats-my-ip/',
                            'http://checkip.dyndns.com/',
                            'http://www.ip-adress.eu/',
                            'http://www.infosniper.net/',
                            'https://wtfismyip.com/text',
                            'http://ipinfo.io/',
                            'http://httpbin.org/ip',
                            'https://diagnostic.opendns.com/myip',
                            'http://checkip.amazonaws.com',
                            'https://api.ipify.org',
                            'https://v4.ident.me']

    def get_externalip(self):
        '''
        This function gets your IP from a random server
        '''

        myip = ''
        for i in range(7):
            myip = self.fetch(random.choice(self.server_list))
            if myip != '':
                return myip
            else:
                continue
        return ''

    def fetch(self, server):
        '''
        This function gets your IP from a specific server.
        '''
        url = None
        cj = cjar.CookieJar()
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        opener = urllib.build_opener(urllib.HTTPCookieProcessor(cj), urllib.HTTPSHandler(context=ctx))
        opener.addheaders = [('User-agent', "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"),
                             ('Accept', "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                             ('Accept-Language', "en-US,en;q=0.5")]

        try:
            url = opener.open(server, timeout=4)
            content = url.read()

            # Didn't want to import chardet. Prefered to stick to stdlib
            if PY3K:
                try:
                    content = content.decode('UTF-8')
                except UnicodeDecodeError:
                    content = content.decode('ISO-8859-1')

            m = re.search(
                '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',
                content)
            myip = m.group(0)
            return myip if len(myip) > 0 else ''
        except Exception:
            return ''
        finally:
            if url:
                url.close()

    def test(self):
        '''
        This functions tests the consistency of the servers
        on the list when retrieving your IP.
        All results should be the same.
        '''

        resultdict = {}
        for server in self.server_list:
            resultdict.update(**{server: self.fetch(server)})

        ips = sorted(resultdict.values())
        ips_set = set(ips)
        print('\nNumber of servers: {}'.format(len(self.server_list)))
        print("IP's :")
        for ip, ocorrencia in zip(ips_set, map(lambda x: ips.count(x), ips_set)):
            print('{0} = {1} ocurrenc{2}'.format(ip if len(ip) > 0 else 'broken server', ocorrencia, 'y' if ocorrencia == 1 else 'ies'))
        print('\n')
        print(resultdict)

if __name__ == '__main__':
    print(myip())
