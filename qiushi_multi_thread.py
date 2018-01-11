# coding=utf-8
import Queue
import re
import threading
import urllib2
import sys

import time

reload(sys)
sys.setdefaultencoding('utf-8')


def get_page(url):
    """
    得到指定页码的内容
    :param url:
    """
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}
    try:
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        content = response.read().decode('utf-8')
        print("成功获取到第%s页内容" % url.split('/')[-1])
        return content
    except urllib2.URLError as e:
        if hasattr(e, "reason"):
            print("连接糗事百科失败%s" % e.reason)
            return None


def get_page_stories(url):
    """
    获取当前页面所有的故事，并加入到List中返回
    :param url:
    """
    print("从get_page_stories方法爬取指定页面的内容")
    page_code = get_page(url)
    if not page_code:
        print("第%s加载失败" % url.split('/')[-1])
        return None
    else:
        pattern = re.compile('<div class="article block untagged .*?" id=.*?>.*?<div class="author clearfix">'
                             + '.*?<a.*?<img.*?alt="(.*?)".*?<a.*?articleGender.*?">(.*?)</div>.*?class="content"'
                             + '.*?<span>(.*?)</span>', re.S)
        items = re.findall(pattern, page_code)
        print("第%s页匹配完成" % url.split('/')[-1])
        page_stories = []
        for item in items:
            item_info = {'name': item[0], 'age': item[1], 'content': item[2].replace("\n", "").replace('<br/>', '')}
            page_stories.append(item_info)
        return page_stories


queue = Queue.Queue()
stories = []
con = threading.Condition()
page_index = 1


class SpiderQSBK(threading.Thread):
    """
    糗事百科爬虫类
    """

    def __init__(self):
        super(SpiderQSBK, self).__init__()

    def run(self):
        """
        爬取内容
        """
        global queue
        global con
        print("执行了consumer run方法")
        while True:
            if con.acquire():
                print("consumer acquire a lock")
                if not queue.empty():
                    url = queue.get()
                    print("正在消费url%s" % url)
                    page_stories = get_page_stories(url)
                    stories.append(page_stories)
                    con.notify()
                    con.release()
                else:
                    print("队列为空, consumer无法消费，将会wait")
                    con.notify()
                    con.wait()
                time.sleep(2)


class Producer(threading.Thread):
    """
    产生任务的线程
    """

    def __init__(self):
        super(Producer, self).__init__()

    def run(self):
        """
        处理生产任务
        """
        global queue
        global page_index
        print("执行了run方法")
        while True:
            if con.acquire():
                if page_index < 14:
                    if queue.qsize() < 4:
                        print("生产了%s" % page_index)
                        queue.put('https://www.qiushibaike.com/hot/page/' + str(page_index))
                        page_index += 1
                        con.notify()
                        con.release()
                        print("锁已经被释放")
                    else:
                        con.notify()
                        con.wait()
                else:
                    con.notify()
                    con.release()
                time.sleep(2)


if __name__ == '__main__':

    for i in range(1, 3):
        producer = Producer()
        producer.start()

    for i in range(1, 4):
        spider = SpiderQSBK()
        spider.start()
