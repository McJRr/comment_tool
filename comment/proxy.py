# -*- coding: utf-8 -*-
import requests
import re
import random
import logging

log = logging.getLogger(__name__)


class Mode:
    RANDOMIZE_PROXY_EVERY_REQUESTS = 'wa'
    RANDOMIZE_PROXY_ONCE = 'wo'
    RANDOMIZE_PROXY_ONCE_GAVE = 'ws'
    RANDOMIZE_LOCAL_REQUESTS = 'la'
    RANDOMIZE_LOCAL_ONCE = 'lo'
    RANDOMIZE_LOCAL_ONCE_GAVE = 'ls'


class RandomProxy(object):
    def __init__(self, settings):
        self.mode = settings.get('PROXY_MODE')  ####   0
        self.chosen_proxy = ''
        self.proxies = {}
        self.gaven_proxy = {}
        if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS or self.mode == Mode.RANDOMIZE_PROXY_ONCE:
            self.proxies = get_proxy_web()
            if self.mode == Mode.RANDOMIZE_PROXY_ONCE:
                self.chosen_proxy = random.choice(list(self.proxies.keys()))
        elif self.mode == Mode.RANDOMIZE_LOCAL_REQUESTS or self.mode == Mode.RANDOMIZE_LOCAL_ONCE:
            self.proxies = get_proxy_local()
            if self.mode == Mode.RANDOMIZE_LOCAL_ONCE:
                self.chosen_proxy = random.choice(list(self.proxies.keys()))
        elif self.mode == Mode.RANDOMIZE_PROXY_ONCE_GAVE:
            for web_cache in settings.get(self.mode):
                self.gaven_proxy[web_cache] = ''
        elif self.mode == Mode.RANDOMIZE_LOCAL_ONCE_GAVE:
            proxy_local_cache = settings.get(self.mode)
            self.gaven_proxy = get_proxy_local_myself(proxy_local_cache)
        log.info("Proxy middleware is enabled.")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS or self.mode == Mode.RANDOMIZE_LOCAL_REQUESTS:
            request.meta['proxy'] = random.choice(list(self.proxies.keys()))
        elif self.mode == Mode.RANDOMIZE_PROXY_ONCE or self.mode == Mode.RANDOMIZE_LOCAL_ONCE:
            request.meta['proxy'] = self.chosen_proxy
        elif self.mode == Mode.RANDOMIZE_PROXY_ONCE_GAVE or self.mode == Mode.RANDOMIZE_LOCAL_ONCE_GAVE:
            request.meta['proxy'] = random.choice(list(self.gaven_proxy.keys()))
        log.info("proxy: %s" % request.meta['proxy'])

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS or self.mode == Mode.RANDOMIZE_LOCAL_REQUESTS or self.mode == Mode.RANDOMIZE_PROXY_ONCE or self.mode == Mode.RANDOMIZE_LOCAL_ONCE:
            proxy = request.meta['proxy']
            try:
                del self.proxies[proxy]
            except KeyError:
                pass
            if len(self.proxies) <= 0:
                if self.mode == Mode.RANDOMIZE_PROXY_EVERY_REQUESTS or self.mode == Mode.RANDOMIZE_PROXY_ONCE:
                    self.proxies = get_proxy_web()
                    if self.mode == Mode.RANDOMIZE_PROXY_ONCE:
                        self.chosen_proxy = random.choice(list(self.proxies.keys()))
                elif self.mode == Mode.RANDOMIZE_LOCAL_REQUESTS or self.mode == Mode.RANDOMIZE_LOCAL_ONCE:
                    self.proxies = get_proxy_local()
                    if self.mode == Mode.RANDOMIZE_LOCAL_ONCE:
                        self.chosen_proxy = random.choice(list(self.proxies.keys()))


def get_proxy_web():
    proxies = {}
    r = requests.get("http://192.168.241.40:15400/?count=200&protocol=0")
    proxy_list = ["http://%s:%s" % (ip, port) for ip, port, score in r.json() if score > 0]
    if proxy_list is None:
        raise KeyError('PROXY_LIST setting is missing')
    for line in proxy_list:
        parts = re.match('(\w+://)(\w+:\w+@)?(.+)', line.strip())
        if not parts:
            continue
        if parts.group(2):
            user_pass = parts.group(2)[:-1]
        else:
            user_pass = ''
        proxies[parts.group(1) + parts.group(3)] = user_pass
    return proxies


def get_proxy_local():
    proxies = {}
    localhost_proxy = [4, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 27, 28, 30, 31,
                       40, 43, 48, 50, 49, 47, 46, 44, 42, 41, 38, 37, 36]
    for m in localhost_proxy:
        proxies["http://b{0}:maixunsquid@192.168.241.{0}:17070".format(m)] = ''
    return proxies


def get_proxy_local_myself(proxy_local_cache):
    proxies = {}
    for m in proxy_local_cache:
        proxies["http://b{0}:maixunsquid@192.168.241.{0}:17070".format(m)] = ''
    return proxies
