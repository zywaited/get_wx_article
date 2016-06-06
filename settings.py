#-*- coding:utf-8 -*-

#数据库连接配置
MYSQL_SETTING = {
                'table' : 'wp_wxarticle_bak',
                'host' : 'localhost',
                'user' : 'root',
                'passwd' : '',
                'db' : 'test',
                'port' : 3306,
                'charset' : 'utf8',
                'time_table' : 'wp_wxarticle',
                'info_table' : 'wp_wxinfo'
                }
#开启mysql命令
MYSQL_COMMAND = ''

#reids连接配置
REDIS_FLAG = False
REDIS_SETTING = {
                'host' : '127.0.0.1',
                'passwd' : '',
                'db' : 0,
                'port' : 6379,
                'charset' : 'utf-8'
                 }

#抓取的最大页码数
PAGE = 1

#进线程数配置
PROCESS_NUM = 3
THREAD_NUM = 2

#文件日志保存路径
FILE_NAME = ''

#是否需要最小时间过滤
LAST_TIME_FLAG = True

#重试次数
AGAIN_NUM = 1

