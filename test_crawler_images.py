#-*- coding=utf-8 -*-

# 目标网站:http://www.wmpic.me/meinv/yindu

from lxml import etree
import requests
import urllib
import os


class CatItem:
    def __init__(self, text, title, href):
        self.text = text
        self.title = title
        self.href = href

#读取美女栏目总共有多少分类
def get_cat_list(url):
    r = requests.get(url)
    #读取请求的编码设置设为当前解析时的编码设置
    r.encoding = r.apparent_encoding
    html = etree.HTML(r.text)
    cat_list = html.xpath("//*[@class='cat-item']")
    result = []
    for item in cat_list:
        a = item.xpath("a")[0]
        text = a.text
        href = a.xpath("@href")[0]
        title = a.xpath("@title")[0]
        cat_item = CatItem(text, title, href)
        result.append(cat_item)
    return result

#读取每个分类下面每一页的数据,每一页包含一个列表,每个列表内部的链接里面的图片才是要解析的
def get_cat_pages(item):
    text = item.text
    href = item.href
    url = url_cat_page % href
    while url:
        #print url
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        html = etree.HTML(r.text)
        item_list = html.xpath("//*[@class='item_list']/li")
        for item in item_list:
            a = item.xpath("div")[0].xpath("a")[0]
            title = a.xpath("@title")[0]
            href = a.xpath("@href")[0]
            get_images(text + "/" + title, href)
            #print title + " " + href 
        #检查是否有下一页
        url = ''
        page = html.xpath("//*[@class='wp-pagenavi']")
        if page:
            page_list = page[0].xpath("a")
            if page_list and page_list[-1].text == '下一页'.decode('utf-8'):
                url = url_home + page_list[-1].xpath("@href")[0]

#每一个详情页里解析图片
def get_images(dir, url):
    #print dir + " " + url
    r = requests.get(url_home + url)
    r.encoding = r.apparent_encoding
    html = etree.HTML(r.text)
    images = html.xpath("//*[@class='content-c']")[0].xpath("p")
    for p in images:
        a = p.xpath('a') 
        if a:
            img = a[0].xpath("img")
            if img:
                 imgurl = img[0].xpath("@src")[0]
                 save_img(dir, imgurl)
    
#保存图片文件
def save_img(dir, url):
    file = url.split('/')[-1]
    dirpath = root_dir + "/" + dir 
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    urllib.urlretrieve(url, dirpath + "/" + file)

#定义一些 url 字符串
url_home = "http://www.wmpic.me"
url_cat = url_home + "/meinv"
url_cat_page= url_home + "/%s/page/1"
url_images = url_home + "/%s"
root_dir = 'images'

#运行起始
cat_list = get_cat_list(url_cat)
for item in cat_list:
    get_cat_pages(item)
