#-*- coding:utf-8 -*-

from multiprocessing import Manager
    
class Queue_server(object):
    
    '''
                 初始话公众号队列
     @param Tuple wx_lists 公众号列表
    '''
    def __init__(self ,wx_lists=()):
        self.__queue = Manager().Queue(-1)
        self.init_wx_lists(wx_lists)
        self.__fail_list = Manager().list()
    '''
                 初始话公众号队列
     @param Tuple wx_lists 公众号列表
    '''      
    def init_wx_lists(self ,wx_lists=()):
        for wx in wx_lists:
            self.put(wx)
    '''
                 添加元素
     @param mixed value 要添加的元素
    '''
    def put(self ,value):
        self.__queue.put(value)
    
    '''
                 弹出元素
     @return mixed       
    '''
    def get(self):
        if not self.__queue.empty():
            return self.__queue.get()
        return False
    
    '''
                 获取队列
     @return mixed       
    '''
    def get_wx_lists_queue(self):
        return self.__queue
    
    '''
                             获取队列大小
        @return int
    '''
    def get_size(self):
        return self.__queue.qsize()
    
    '''
                             队列是否为空
        @return bool
    '''
    def empty(self):
        return self.__queue.empty()
    
    '''
                             添加失败数据
        @param tuple wx_data 公众号信息
        @return bool
    '''     
    def put_fail_wx(self , wx_data):
        self.__fail_list.append(wx_data)
    
    '''
                             打印失败列表
    '''    
    def print_fail_list(self ,flush=None):
        if len(self.__fail_list) > 0:
            for fail in self.__fail_list:
                self.put(fail)
                print 'the fail wx : {0}' . format(fail)
            if not flush:
                self.__fail_list = Manager().list()
        elif flush:
            print 'all success'
            
    #判断是否有错
    def is_have_failed(self):
        return len(self.__fail_list)