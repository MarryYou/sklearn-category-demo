# coding:utf-8
import requests
from bs4 import BeautifulSoup
import time
import re
from database import DataBaseClient


class crawlSpider():
    #一个简单的爬虫类 用于爬取机器学习 的实验数据 
    def __init__(self, headers):
        self.headers = headers

    def startparse(self, url, category):
        try:
            res = requests.get(
                url=url, headers=self.headers)
            if res.status_code == 200:
                res.encoding = 'utf-8'
                links = []
                html = BeautifulSoup(res.text, 'lxml').find_all(
                    'ul', class_='tbody')[0].find_all('a', class_='meiwen')
                for title in html:
                    links.append({'url': 'https://www.meiwen.com.cn' +
                                  title['href'], 'title': title.text, 'category': category})
                print('url get success')
                return links
        except Exception as e:
            print(e)

    def articleparse(self, url, title, category):
        try:
            res = requests.get(url=url, headers=self.headers)
            if res.status_code == 200:
                html = BeautifulSoup(res.text, 'lxml').find_all(
                    'div', class_='content')[0]
                print('get content success')
                return{'title': title, 'content': html.text, 'category': category}
        except Exception as e:
            print(e)


def main():

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    client = DataBaseClient('localhost', 27017)
    client.setDB('meiwenshare')
    client.setCollection('articles')
    web = crawlSpider(headers)
    first_urls = [
        {'url': 'https://www.meiwen.com.cn/wenzhang/lizhi/','category': 'motivational'},
        {'url': 'https://www.meiwen.com.cn/wenzhang/aiqing/', 'category': 'love'},
        {'url': 'https://www.meiwen.com.cn/wenzhang/qinqing/', 'category': 'family'},
        {'url': 'https://www.meiwen.com.cn/wenzhang/youqing/', 'category': 'friendship'},
        {'url': 'https://www.meiwen.com.cn/wenzhang/xinqing/', 'category': 'mood'}]
    for url in first_urls:
        #这里的数据爬取3:7分是人工分类 监督机器学习，第一次写这些 不专业见谅
        for i in range(0, 10):
            if i < 7:
                links = web.startparse(
                    url['url']+str(i)+'.html', url['category'])  # 这里的文章分类属于以上爬虫的文章分类
                for j in links:
                    data = web.articleparse(j['url'], j['title'], j['category'])
                    if data:
                        client.add_one(data)
                        print('insert data success')
            else:
                links = web.startparse(url['url']+str(i)+'.html', 'other')#这里的文章分类属于其他
                for j in links:
                    data = web.articleparse(j['url'], j['title'], 'other')
                    if data:
                        client.add_one(data)
                        print('insert data success')                       
if __name__ == '__main__':
    main()
