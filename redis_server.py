#-*- coding:utf-8 -*-

import redis
from settings import REDIS_SETTING

class Redis_server(object):
    
    '''
                             初始化
        @param String host 主机名
        @param String port 端口号
        @param String db 数据库名
        @param String password 密码
        @param String charset 字符集
    '''
    def __init__(self ,host=REDIS_SETTING['host'] ,port=REDIS_SETTING['port'] ,db=REDIS_SETTING['db'] ,password=REDIS_SETTING['passwd'] ,encoding=REDIS_SETTING['charset']):
        self.__redis = redis.StrictRedis(host=host ,port=port ,db=db ,password=password ,encoding=encoding)
        self.__fail_list = 'fail_wx_list'
        self.__list = 'wx_list'
        self.__flag = 'wx_init_flag'
        self.__fail_len = 0
    
    '''
                 初始话公众号队列
     @param Tuple wx_lists 公众号列表
    '''      
    def init_wx_lists(self ,wx_lists=()):
        if not self.__redis.get(self.__flag):
            for wx in wx_lists:
                self.put(wx)
            self.__redis.set(self.__flag ,1)
                
    '''
                 添加元素
     @param mixed value 要添加的元素
    '''
    def put(self ,value):
        self.__redis.rpush(self.__list ,value)
    
    '''
                 弹出元素
     @return mixed       
    '''
    def get(self):
        if self.get_size():
            return eval(self.__redis.lpop(self.__list))
        return False
    
    '''
                 获取队列
     @return list       
    '''
    def get_wx_lists_queue(self):
        return self.__redis.lrange(self.__list ,0 ,-1)   
        
    '''
                             获取队列大小
        @return int
    '''
    def get_size(self):
        return self.__redis.llen(self.__list)
    
    '''
                             队列是否为空
        @return bool
    '''
    def empty(self):
        return self.get_size() <= 0
    
    '''
                             添加失败数据
        @param tuple wx_data 公众号信息
        @return bool
    '''     
    def put_fail_wx(self , wx_data):
        self.__redis.rpush(self.__fail_list ,wx_data)
    
    '''
                             打印失败列表并且清空
    '''    
    def print_fail_list(self ,flush=None):
        self.__fail_len = self.__redis.llen(self.__fail_list)
        if self.__fail_len > 0:
            print ''
            for i in range(self.__fail_len):
                print 'the fail wx : {0}' . format(self.__redis.rpoplpush(self.__fail_list ,self.__list))
        elif flush:
            self.__flush()
            print 'all success'
    
    '''
                             删除
        @param string name 名称
    '''
    def delete(self ,name):
        self.__redis.delete(name)
        
    def __flush(self):
        self.delete(self.__fail_list)
        self.delete(self.__list)
        self.delete(self.__flag)
    
    #查看是否有错  
    def is_have_failed(self):
        return self.__fail_len
    