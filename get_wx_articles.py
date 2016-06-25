#-*- coding:utf-8 -*-
from lxml import html
import re
import requests
import time
import random
import json
from settings import PAGE,LAST_TIME_FLAG,PROCESS_NUM,THREAD_NUM,AGAIN_NUM,MYSQL_COMMAND
from mysql_server import Mysql_db
from create_queue import create_queue
from multiprocessing import Pool
import threading
# import sys
import subprocess

#requests session 文章抓取变量
s_article = None

#requests session 图片抓取变量
s_img = None

#数据库变量
db = None
try_lock = None
try_flag = False

#队列变量以及标志
rq = None
rq_type = None

#全局文章是否符合标志
#article_flag = True

#最小时间点
last_time = 0

#初始化
def init():
    init_requests_article()
    init_requests_img()
    init_mysql_server()
    db.truncate()
    init_wx_lists()    

#初始化requests_article
def init_requests_article():
    global s_article
    s_article = requests.Session()
    headers = {
               'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0',
               'Host' : 'www.gsdata.cn',
               'Referer' : 'http://www.gsdata.cn'
               }
    s_article.headers.update(headers)
#     return s_article

#初始化requests_img
def init_requests_img():
    global s_img
    s_img = requests.Session()
    headers = {
                'Host' : 'img1.gsdata.cn',
                'Referer' : 'http://www.gsdata.cn',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat'
               }
    s_img.headers.update(headers)
#     return s_img

#初始化mysql and 最小时间
def init_mysql_server():
    global db,last_time
    sub = None
    
    #标志是否正在启动mysql
    flag = False
    while True:
        try:  
            db = Mysql_db()
            if LAST_TIME_FLAG and not last_time:
                last_time = db.get_last_time()
            if sub:
                sub.kill()
            return True
        except:
            print 'the Mysql connection is error , please start mysql server ,but now is starting and connect later(10 sec)'
            if not flag:
                sub = subprocess.Popen(MYSQL_COMMAND ,shell=True)
                flag = True
            print 'the mysql server is starting ...'
            #10sec后进行重试
            time.sleep(10)
            print 'try to connect now ...'
#             sys.exit()
      
#初始化公众号队列
def init_wx_lists():
    global rq,rq_type
    tmp = create_queue(db.get_all_wx())
    rq = tmp[0]
    rq_type = tmp[1]

'''
              输出某个公众号遗失了文章
    @param Int id_index 微信公众号主键id
    @param String typeof 出错地方
'''
def print_pass_a_article(id_index,typeof):
    raise Exception('pass a article and the wx_id_index is {0} and the type_error is {1}' . format(id_index,typeof))

'''
               获取当前公共号的文章信息
    @param String article_html html信息
    @param Int id_index 微信公众号主键id
    @return list
'''
def get_wx_article_lists(article_html,id_index):
    # global article_flag
    #总数据列表
    wx_article_list = []
    
    html_tree = html.document_fromstring(article_html)
    html_nodes = html_tree.xpath('//ul[@class="article-ul"]//li')
    
    for html_node in html_nodes:
        #当前页码的数据字典
        wx_article_object = {}
        
        html_node_children = html_node.getchildren()
         
        #发布时间、赞与阅读量、标题以及简介内容(注：此处最好使用find查找，不然原创文章抓取出错)
        div_wx_ft_children = html_node_children[1].find('div[@class="wx-ft"]').getchildren()
        pub_time = div_wx_ft_children[1].text_content().strip()
        pub_time = pub_time.encode('utf-8').split('：')
        if len(pub_time) < 2:
            print_pass_a_article(id_index,'time')
        else:
            pub_time = int(time.mktime(time.strptime(pub_time[1],'%Y-%m-%d %H:%M:%S')))
            #判断时间是否合理
            if pub_time <= last_time:
                # article_flag = False
#                 print 'out of the time and return'
                return wx_article_list            
        wx_article_object['time'] = str(pub_time)
        readnum_and_likenum = re.split(r'\s',div_wx_ft_children[2].text_content().strip())
        length = len(readnum_and_likenum)
        if length < 2:   
            print_pass_a_article(id_index,'readnum_and_likenum')
        readnum = str(readnum_and_likenum[0]).strip()
        wx_article_object['readnum'] = str(int(readnum))
        likenum = str(readnum_and_likenum[length-1]).strip()
        wx_article_object['likenum'] = str(int(likenum))
    
        div_wx_ft_h4 = html_node_children[1].find('h4')
        title = div_wx_ft_h4.find('a').text_content()
        if not title:
            print_pass_a_article(id_index,'title')
        wx_article_object['title'] = title
        content = div_wx_ft_h4.getnext().text_content()
        if not content:
            print_pass_a_article(id_index,'content')
        wx_article_object['content'] = content
         
        #url、img-data-hash
        div_wx_img_a = html_node_children[0].find('a')
        url = div_wx_img_a.get('href')
        if not url:
            print_pass_a_article(id_index,'url')
        wx_article_object['url'] = url
        img_hash = div_wx_img_a.find('img').get('data-hash')
        if not img_hash:
            print_pass_a_article(id_index,'img-hash')
        wx_article_object['imglink'] = get_img_link(img_hash)
        wx_article_object['id'] = str(int(id_index))
        
        wx_article_list.append(wx_article_object)
    return wx_article_list
        
'''
               获取当前公众号当前页的文章页面
    @param String wx 微信公众号
    @param Int page 页码
    @return String
'''
def get_wx_article_html(wx,page = 1):
    # if last_time:
    #    url = 'http://www.gsdata.cn/query/article?q={0}&sort=-1&search_field=4&page={1}'
    # else:
    #    url = 'http://www.gsdata.cn/query/article?q={0}&post_time=0&sort=-1&search_field=4&page={1}'
    url = 'http://www.gsdata.cn/query/article?q={0}&post_time=0&sort=-1&search_field=4&page={1}' . format(wx,page)
    result = s_article.get(url)
    result.encoding = 'utf-8'
    return result.text

'''
               获取文章的图片链接
    @param String img_hash 图片的hash值
    @return String
'''
def get_img_link(img_hash):
    result = s_img.get('http://img1.gsdata.cn/index.php/rank/getImageUrl?callback=jQuery&hash={0}&_={1}' . format(img_hash,int(time.time())))
    result.encoding = 'utf-8'
    return json.loads(result.text[result.text.find('{') : result.text.rfind('}') + 1])['url']

'''
            当前公众号所有页面的文章信息存入数据库中
    @param String wx 微信公众号
    @param Int id_index 微信公众号主键id
    @return Void
'''
def merge_article_data(wx_data):
    global try_flag
    page_num = 1
    while page_num <= PAGE:
        try:
            tmp_len = len(wx_data)
            if tmp_len > 2:
                page_num = wx_data[tmp_len - 1]
            article_html = get_wx_article_html(wx_data[0], page_num)
            data_objects = get_wx_article_lists(article_html,wx_data[1])
            fetch_num = len(data_objects)
            if fetch_num >= 1:
                try:
                    insert_num  = db.query_all(data_objects)
                except:
                    try_lock.acquire()
                    #此处出现2006或者2013，需要重连一次mysql
                    if not try_flag:
                        db.connect()
                        try_flag = True
                    try_lock.release()
                    time.sleep(1)
                    insert_num  = db.query_all(data_objects)
                print 'the wx : {0} and the wx_id : {1} and the page : {2} ; and insert_num : {3}' . format(wx_data[0] , wx_data[1] ,page_num ,insert_num)
                if not insert_num:
                    wx_data = wx_data + (page_num,)
                    rq.put_fail_wx(wx_data)
                else:
                    if try_flag:
                        try_flag = False
            else:
    #             raise Exception('the wx_article_list fetch is false')
                print 'the wx : {0} and the wx_id : {1} and the page : {2} is out of the time or null' . format(wx_data[0] , wx_data[1] ,page_num)
            time.sleep(random.randint(1,5))
            if fetch_num < 20:
                return
            page_num += 1
        except Exception as e:
            wx_data = wx_data + (page_num,)
            rq.put_fail_wx(wx_data)
            print e
            time.sleep(random.randint(1,5))
            return 
'''
             创建线程
    @param requests.session s_article_bak 文章爬虫
    @param requests.session s_img_bak 图片爬虫
    @param int last_time_bak 最小时间 
    @param queue.server queue 公众号队列 
'''
def create_thread(s_article_bak ,s_img_bak ,last_time_bak ,queue=None): 
    global try_lock
    if not try_lock:
        try_lock = threading.Lock()
    if PROCESS_NUM:
        #资源不共享，在进程中重新声明
        global s_article,s_img,last_time,rq
        
        #Mysql_db类不能被系列化，所有只有重新初始化
        init_mysql_server()
        if not queue:
            init_wx_lists()
        else:
            rq = queue
        s_article = s_article_bak
        s_img = s_img_bak
        last_time = last_time_bak
    else:
        rq = queue
     
    thread_list = []
    thread_flag = True
    while thread_flag:
        for i in xrange(THREAD_NUM):
            wx_data = rq.get()
            if wx_data:
                print 'the wx is {0} and the thread : {1} has started' . format(wx_data[0], i)
                t = threading.Thread(target=merge_article_data ,args=(wx_data,))
                t.start()
                thread_list.append(t)
            else:
                thread_flag = False
        for t in thread_list:
            t.join()
       
    db.close_all()  
    
'''
              创建进程 
''' 
def create_process():
    if PROCESS_NUM:
        process_pools = Pool(processes=PROCESS_NUM)
        for i in xrange(PROCESS_NUM):
            if rq_type:
                process_pools.apply_async(create_thread ,(s_article,s_img,last_time,None))
            else:
                process_pools.apply_async(create_thread ,(s_article,s_img,last_time,rq))
            print '第  {0} 个进程启动' . format(i+1)
        process_pools.close()
        process_pools.join()
    else:
        create_thread(s_article,s_img,last_time)
    rq.print_fail_list(None)

if __name__ == '__main__':
    init()
    print 'all init_tasks is successful'
    create_process()
    while AGAIN_NUM and rq.is_have_failed():
        AGAIN_NUM -= 1
        print ''
        print '现在开始进行重试   ;  剩余次数：{0}' . format(AGAIN_NUM)
        create_process()
          
    rq.print_fail_list(True)
    
    