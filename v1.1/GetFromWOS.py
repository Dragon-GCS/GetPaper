#!/usr/bin/env python3
# Dragon's Code
# encoding = utf-8
# date = 20200911
# 1.文章信息界面信息读取，除原文链接外全部完成
# 2.搜索结果页面解析获取文章页面
# 3.网页使用JS语法，或可以从搜索结果页直接获取除doi外所有信息

import urllib.request as ur
from http import cookiejar
from math import ceil
from re import sub
from bs4 import BeautifulSoup


class GetFromWOS:
    def __init__(self):
        self.keyword = ''
        self.paper_number = 0
        # 创建PMID、标题、作者、期刊、日期、摘要、网址、doi列表
        self.address = []
        self.title_list = []
        self.author_list = []
        self.publication_list = []
        self.date_list = []
        self.abstract_list = []
        self.web_list = []
        self.doi_list = []
        # 缓存网页信息
        self.html = ''

        self.opener = opener_creat()
        self.base_url = 'http://apps.webofknowledge.com'
        self.header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/80.0.3987.132 Safari/537.36'}
        # 文献搜索提示数量
        self.count = 0

    def open_html(self, url, timeout=15):
        req = ur.Request(url, headers=self.header)
        response = self.opener.open(req, timeout=timeout)
        html = response.read()
        return html

    def get_paper_max_num(self, page=1, size=100):
        keyword = sub(r'\W', '+', self.keyword)
        # 合成网址
        url = self.base_url + '?term=' + keyword + '&size=' + str(size) + '&page=' + str(page)
        self.html = self.open_html(url)
        bs = BeautifulSoup(self.html, 'lxml')
        # 获取找到的文献总数
        paper_max_num = bs.find(id='trueFinalResultCount').string
        return paper_max_num

    def get_address(self):
        bs = BeautifulSoup(self.html, 'lxml')
        for tag in bs.find_all(class_='search-results-content'):
            self.address.append(self.base_url + tag.a['href'])
        if len(self.address) > self.paper_number:
            self.address = self.address[:self.paper_number]
            print('获取网址信息%s个' % len(self.address))

    def get_content(self, pmid):
        try:
            bs = BeautifulSoup(self.open_html(pmid), 'lxml')
            self.title_list.append(bs.find(class_='title').text[1:-1])
            self.author_list.append(sub(r'\n|\s+', '',
                                        bs.find(title="Find more records by this author").parent.text[4:]))
            self.publication_list.append(bs.find(class_='sourceTitle').text[1:-1])
            self.date_list.append(bs.find(text='Published:').parent.parent.value.string)
            self.abstract_list.append(bs.find(class_='title3').parent.p.text)
            self.web_list.append(bs.find(id='oa_ac_tag_4').a['href'])
            self.doi_list.append(bs.find(attrs={'name': 'doi'}).string)
        except Exception as e:
            print('错误原因：' + str(e))
            print('错误文献：%s,第%d篇' % (self.address[self.count - 1], self.count))
            self.title_list.append('Unconnected')
            self.author_list.append('Unconnected')
            self.publication_list.append('Unconnected')
            self.date_list.append('Unconnected')
            self.abstract_list.append('Unconnected')
            self.web_list.append(pmid)
            self.doi_list.append('Unconnected')

    def main(self, num):
        self.paper_number = int(num)
        # 确认PMID列表
        self.get_address()
        page = ceil(self.paper_number / 100)
        if page - 1:
            for i in range(2, page + 1):
                self.get_paper_max_num(page=i)
                self.get_address()
        for pmid in self.address:
            self.count += 1
            print('正在获取第%i篇,共计%s篇' % (self.count, len(self.address)))
            self.get_content(pmid)
        print('获取完成')

    def run_it(self):
        self.keyword = input('请输入需要查询的关键词：')
        print('开始在PubMed上查找关键词为“%s”的文献……' % self.keyword)
        if self.get_paper_max_num():
            print('共查找到%s篇文献' % self.get_paper_max_num())
            num = input('请输入需要获取信息的文献数量：')
            print('开始获取')
            self.main(num)

        else:
            print('未找到相关文献')


def opener_creat():
    # 创建cookie
    cookie = cookiejar.CookieJar()
    cookie_handler = ur.HTTPCookieProcessor(cookie)
    http_handler = ur.HTTPHandler()
    https_handler = ur.HTTPSHandler()
    opener = ur.build_opener(cookie_handler, http_handler, https_handler)
    return opener
