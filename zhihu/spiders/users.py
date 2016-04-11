# -*- coding: utf-8 -*-
import scrapy
import os
import time
from zhihu.items import UserItem
from zhihu.myconfig import UsersConfig

class UsersSpider(scrapy.Spider):
    name = 'users'
    domain = 'https://www.zhihu.com'
    login_url = 'https://www.zhihu.com/login/email'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "www.zhihu.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36"
    }

    def __init__(self, url = None):
        self.user_url = url

    def start_requests(self):
        yield scrapy.Request(
            url = self.domain,
            headers = self.headers,
            meta = {
                'proxy': UsersConfig['proxy'],
                'cookiejar': 1
            },
            callback = self.request_captcha
        )

    def request_captcha(self, response):
        # 获取_xsrf值
        _xsrf = response.css('input[name="_xsrf"]::attr(value)').extract()[0]
        # 获取验证码地址
        captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + str(time.time() * 1000)
        # 准备下载验证码
        yield scrapy.Request(
            url = captcha_url,
            headers = self.headers,
            meta = {
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                '_xsrf': _xsrf
            },
            callback = self.download_captcha
        )

    def download_captcha(self, response):
        # 下载验证码
        with open('captcha.gif', 'wb') as fp:
            fp.write(response.body)
        # 用软件打开验证码图片
        os.system('start captcha.gif')
        # 输入验证码
        print 'Please enter captcha: '
        captcha = raw_input()

        yield scrapy.FormRequest(
            url = self.login_url,
            headers = self.headers,
            formdata = {
                'email': UsersConfig['email'],
                'password': UsersConfig['password'],
                '_xsrf': response.meta['_xsrf'],
                'remember_me': 'true',
                'captcha': captcha
            },
            meta = {
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar']
            },
            callback = self.request_zhihu
        )

    def request_zhihu(self, response):
        yield scrapy.Request(
            url = self.user_url + '/about',
            headers = self.headers,
            meta = {
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                'from': {
                    'sign': 'else',
                    'data': {}
                }
            },
            callback = self.user_item,
            dont_filter = True
        )

        yield scrapy.Request(
            url = self.user_url + '/followees',
            headers = self.headers,
            meta = {
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                'from': {
                    'sign': 'else',
                    'data': {}
                }
            },
            callback = self.user_start,
            dont_filter = True
        )

        yield scrapy.Request(
            url = self.user_url + '/followers',
            headers = self.headers,
            meta = {
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                'from': {
                    'sign': 'else',
                    'data': {}
                }
            },
            callback = self.user_start,
            dont_filter = True
        )

    def user_start(self, response):
        sel_root = response.xpath('//h2[@class="zm-list-content-title"]')
        # 判断关注列表是否为空
        if len(sel_root):
            for sel in sel_root:
                people_url = sel.xpath('a/@href').extract()[0]

                yield scrapy.Request(
                    url = people_url + '/about',
                    headers = self.headers,
                    meta = {
                        'proxy': UsersConfig['proxy'],
                        'cookiejar': response.meta['cookiejar'],
                        'from': {
                            'sign': 'else',
                            'data': {}
                        }
                    },
                    callback = self.user_item,
                    dont_filter = True
                )

                yield scrapy.Request(
                    url = people_url + '/followees',
                    headers = self.headers,
                    meta = {
                        'proxy': UsersConfig['proxy'],
                        'cookiejar': response.meta['cookiejar'],
                        'from': {
                            'sign': 'else',
                            'data': {}
                        }
                    },
                    callback = self.user_start,
                    dont_filter = True
                )

                yield scrapy.Request(
                    url = people_url + '/followers',
                    headers = self.headers,
                    meta = {
                        'proxy': UsersConfig['proxy'],
                        'cookiejar': response.meta['cookiejar'],
                        'from': {
                            'sign': 'else',
                            'data': {}
                        }
                    },
                    callback = self.user_start,
                    dont_filter = True
                )

    def user_item(self, response):
        def value(list):
            return list[0] if len(list) else ''

        sel = response.xpath('//div[@class="zm-profile-header ProfileCard"]')

        item = UserItem()
        item['url'] = response.url[:-6]
        item['name'] = sel.xpath('//a[@class="name"]/text()').extract()[0].encode('utf-8')
        item['bio'] = value(sel.xpath('//span[@class="bio"]/@title').extract()).encode('utf-8')
        item['location'] = value(sel.xpath('//span[contains(@class, "location")]/@title').extract()).encode('utf-8')
        item['business'] = value(sel.xpath('//span[contains(@class, "business")]/@title').extract()).encode('utf-8')
        item['gender'] = 0 if sel.xpath('//i[contains(@class, "icon-profile-female")]') else 1
        item['avatar'] = value(sel.xpath('//img[@class="Avatar Avatar--l"]/@src').extract())
        item['education'] = value(sel.xpath('//span[contains(@class, "education")]/@title').extract()).encode('utf-8')
        item['major'] = value(sel.xpath('//span[contains(@class, "education-extra")]/@title').extract()).encode('utf-8')
        item['employment'] = value(sel.xpath('//span[contains(@class, "employment")]/@title').extract()).encode('utf-8')
        item['position'] = value(sel.xpath('//span[contains(@class, "position")]/@title').extract()).encode('utf-8')
        item['content'] = value(sel.xpath('//span[@class="content"]/text()').extract()).strip().encode('utf-8')
        item['ask'] = int(sel.xpath('//div[contains(@class, "profile-navbar")]/a[2]/span[@class="num"]/text()').extract()[0])
        item['answer'] = int(sel.xpath('//div[contains(@class, "profile-navbar")]/a[3]/span[@class="num"]/text()').extract()[0])
        item['agree'] = int(sel.xpath('//span[@class="zm-profile-header-user-agree"]/strong/text()').extract()[0])
        item['thanks'] = int(sel.xpath('//span[@class="zm-profile-header-user-thanks"]/strong/text()').extract()[0])

        yield item
