# coding=utf-8
import re
import urllib2

import sys

import time

reload(sys)
sys.setdefaultencoding('utf-8')


def get_page(page_index):
    """
    得到指定页码的内容
    :param page_index:
    """
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}
    try:
        url = 'https://www.qiushibaike.com/hot/page/' + str(page_index)
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        content = response.read().decode('utf-8')
        print("成功获取到第%d页内容" % page_index)
        return content
    except urllib2.URLError as e:
        if hasattr(e, "reason"):
            print("连接糗事百科失败%s" % e.reason)
            return None


def get_page_stories(page_index):
    """
    获取当前页面所有的故事，并加入到List中返回
    :param page_index:
    """
    print("从get_page_stories方法爬取指定页面的内容")
    page_code = get_page(page_index)
    if not page_code:
        print("第%d加载失败" % page_index)
        return None
    else:
        pattern = re.compile('<div class="article block untagged .*?" id=.*?>.*?<div class="author clearfix">'
                             + '.*?<a.*?<img.*?alt="(.*?)".*?<a.*?articleGender.*?">(.*?)</div>.*?class="content"'
                             + '.*?<span>(.*?)</span>', re.S)
        items = re.findall(pattern, page_code)
        print("第%d页匹配完成" % page_index)
        page_stories = []
        for item in items:
            item_info = {'name': item[0], 'age': item[1], 'content': item[2].replace("\n", "").replace('<br/>', '')}
            page_stories.append(item_info)
        return page_stories


class SpiderQSBK(object):
    """
    糗事百科爬虫类
    """

    def __init__(self):
        self.page = 1
        self.stories = []
        self.end = False

    def load_page(self):
        """
        将新的一页的故事添加到列表中
        """
        page_stories = get_page_stories(self.page)
        if not page_stories:
            self.end = True
        else:
            self.stories.append(page_stories)

    def add_page_automatically(self):
        """
        自增页码
        """
        self.page += 1

    def crawl(self):
        """
        爬取内容
        """
        while not self.end and self.page < 14:
            # 如果还有页面，就循环爬取
            print("当前页面%d" % self.page)
            self.load_page()
            self.add_page_automatically()
        return self.stories


if __name__ == '__main__':
    t = time.time()
    start = (int(t))
    spider = SpiderQSBK()
    spider.crawl()
    t = time.time()
    end = (int(t))
    print(end - start)
    for items in spider.stories:
        for item in items:
            print(item['name'])
