#-*- coding:utf-8 -*-

import MySQLdb
from settings import MYSQL_SETTING,FILE_NAME
# import time

class Mysql_db(object):
    
    '''
                             初始化
        @param String table 表名
        @param String host 主机名
        @param String user 用户名
        @param String passwd 密码
        @param String db 数据库名
        @param String port 端口号
        @param String charset 字符集
        @param String file_name 文件路径
    '''
    def __init__(self ,table=MYSQL_SETTING['table'] ,host=MYSQL_SETTING['host'] ,user=MYSQL_SETTING['user'] ,passwd=MYSQL_SETTING['passwd'] ,db=MYSQL_SETTING['db'] ,port=MYSQL_SETTING['port'] ,charset=MYSQL_SETTING['charset'] ,file_name=FILE_NAME):
        self.__table = table
        self.connect(host, user, passwd, db, port, charset)
        #文件句柄
        self.__file_opener = None
        if file_name:
            self.init_file_opener(file_name)
        
        #保存keys的值，防止出现不匹配的情况
        self.__keys_list = []
    
    '''
                             连接mysql
        @param String host 主机名
        @param String user 用户名
        @param String passwd 密码
        @param String db 数据库名
        @param String port 端口号
        @param String charset 字符集
    '''
    def connect(self,host=MYSQL_SETTING['host'] ,user=MYSQL_SETTING['user'] ,passwd=MYSQL_SETTING['passwd'] ,db=MYSQL_SETTING['db'] ,port=MYSQL_SETTING['port'] ,charset=MYSQL_SETTING['charset']):
        self.__db = MySQLdb.connect(host ,user ,passwd ,db ,port)
        self.__db_cursor = self.__db.cursor()
        self.__db.set_character_set(charset)
    
    '''
                             执行查询
        @param String sql 查询语句
        @return mix
    '''
    def query(self ,sql):
        try :
            self.__db_cursor.execute(sql)
            return self.__db_cursor.rowcount   
        except MySQLdb.Error as e:
            raise 'Mysql Error %d: %s' % (e.args[0], e.args[1])
            return False
    
    '''
                             获取一行
        @param String sql 查询语句
        @return mix
    '''
    def get_one(self ,sql):
        if self.query(sql):
            return self.__db_cursor.fetchone()
        return False
    
    '''
                             获取所有行
        @param String sql 查询语句
        @return mix
    '''
    def get_all(self ,sql):
        if self.query(sql):
            return self.__db_cursor.fetchall()
        return False
    
    '''
                             一次性执行某个查询
        @param List list_data 数据列表 [{'key':'value'},.....]
        @return mix
    '''
    def query_all(self ,list_data):
        if len(list_data) > 0:
            for index,data in enumerate(list_data):
                if not index:
                    sql = 'insert into {0} ({1}) values ' .format(self.__table ,self.__keys(data))
                sql += '(\'{0}\'),' . format(self.__values(data))
            
            sql = sql . rstrip(',')
            print sql
#             return 0
            #有可能插入出现冲突导致失败，重试一次
            return self.query(sql)
#             if insert_num:
#                 return insert_num
            #睡眠1s
#             time.sleep(1)
#             return self.query(sql)
#             raise Exception('mysql insert error')
#             return 0
        return False
    
    '''
                             获取最小时间
        @return int
    '''
    def get_last_time(self):
        sql = 'select time from {0} order by aid desc limit 1' . format(MYSQL_SETTING['time_table'])
        last_time = self.get_one(sql)
        if last_time:
            return last_time[0]
        return 0
    
    '''
                             获取所有的公众号
        @return tuple
    '''
    def get_all_wx(self):
        sql = 'select wx,id from {0} where is_exist=1' . format(MYSQL_SETTING['info_table'])
        return self.get_all(sql)
   
    def commit(self):
        self.__db.commit()
    
    def rollback(self):
        self.__db.rollback()
    
    def close_all(self):
        self.commit()
        self.__db_cursor.close()
        self.__db.close()
        self.__close_file()
        
    '''
                          初始化文件
        @param String file_name 文件路径
    '''
    def __init_file_opener(self ,file_name):
        self.__file_opener = open(file_name ,'a+')
    
    '''
                             记录日志
        @param String str_log 需要记录的语句
    '''
    def log(self ,str_log):
        if self.__file_opener:
            self.__file_opener.write(str_log)
    #关闭文件
    def __close_file(self):
        if self.__file_opener:
            self.__file_opener.close()
    
    '''
                            实现字符串join和字典的keys方法
        @param dict data 数据
        @return string 
    '''
    def __keys(self ,data):
        keys = ''
        for key in data:
            if key not in self.__keys_list:
                self.__keys_list.append(key)
            keys += ',' + str(key)
        return keys.lstrip(',')
    
    '''
                            实现字符串join和字典的values方法
        @param dict data 数据
        @return string 
    '''
    def __values(self ,data):
        values = ''
        for key in self.__keys_list:
            values += data[key].encode('utf-8') + "','" 
        return values.rstrip(",'")
    
    #清空表
    def truncate(self):
        self.query('truncate {0}' . format(self.__table))
