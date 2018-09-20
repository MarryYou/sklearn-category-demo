# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import jieba
from jieba import analyse
from database import DataBaseClient
import numpy as np
from sklearn import metrics
from sklearn.svm import SVC
import re
client = DataBaseClient('localhost', 27017)


def get_segment():
    #这里通过了jieba中文分词,剔除了未知的会影响结果的字符
    client.setDB('meiwenshare')
    client.setCollection('articles')
    corpus = []
    cursor = client.get_many({})
    for cur in cursor:
        # print('cutting %s\n'%cur['title'])
        #这里是正则替换一些标点符号和不可见字符
        seg_list = jieba.cut(re.sub(
            '[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*：:-《》（）；]+', '', cur['content']))
        line = ''
        for str in seg_list:
            line = line + ' '+str
        print('join success')
        corpus.append(
            {'splitcontent': line, 'oldcontent': cur['content'], 'category': cur['category'], 'title': cur['title']})
    client.setDB('splitwords')
    client.setCollection('feature')
    client.add_many(corpus)
    #添加到另一个用于存储分词切割好的db


def classify():
    client.setDB('splitwords')
    client.setCollection('feature')
    category_ids = range(0, 5)
    category = {}
    category[0] = 'motivational'
    category[1] = 'love'
    category[2] = 'family'
    category[3] = 'friendship'
    category[4] = 'mood'
    corpus = []
    #这里一共分为5类 简单标识为1,2,3,4,5

    for category_id in category_ids:
        #这里是循环从数据库中拿到当前的这一分类的所有的分词完成的文章 然后拼接成为当前分类的语料库
        cursor = client.get_many({'category': category[category_id]})
        line = ''
        for result in cursor:
            segment = result['splitcontent']
            line += " "+segment
        corpus.append(line)  # 这里是保存了5大分类的语料库
    cursor = client.get_many({'category': 'other'})  # 这里是获取最开始爬虫未分类的文章
    line = ''
    update_ids = []  # 为了记录所有未分类的element 的id
    update_titles = []  # 为了记录所有未分类的element 的title
    need_predict = False  # 默认是否需要机器学习自动分类的flag
    for result in cursor:
        id = result['_id']
        update_ids.append(id)
        segment = result['splitcontent']
        title = result['title']
        update_titles.append(title)
        corpus.append(segment)
        need_predict = True
    if False == need_predict:  # 防止没有数据 造成异常
        return
    #计算tfidf的值
    vectorizer = CountVectorizer()
    csr_mat = vectorizer.fit_transform(corpus)
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(csr_mat)
    #这里 词 和 tfidf 值的array
    y = np.array(category_ids)
    #这里是一个分类名称的数组
    model = SVC()
    model.fit(tfidf[0:5], y)  # 用数组的前5行已经分类的数据做模型训练
    predicted = model.predict(tfidf[5:])  # 然后对之后的未分类的信息做分类预测
    for index in range(0, len(update_ids)):  # 这里是把机器学习的自动分类信息重写到数据库中
        update_id = update_ids[index]
        predicted_category = category[predicted[index]]
        with open('result.txt', 'a+', encoding='utf-8') as f:
            data = 'update_id:%s title:%s <=========================================>category:%s\n' % (
                update_id, update_titles[index], predicted_category)
            print(data)  # 为了方便观察 这里我把title id 和自动分类 存到了txt 中
            f.write(data)
        client.update_one({'_id': update_id}, {
                          '$set': {"category": predicted_category}})


def main():
    get_segment()
    #这里是分词的函数
    classify()
    #这里是模型训练然后预测的函数


if __name__ == '__main__':
    main()
