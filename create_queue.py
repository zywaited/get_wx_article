#-*- coding:utf-8 -*-

from settings import REDIS_FLAG

if REDIS_FLAG:
    from redis_server import Redis_server
else:
    from queue_server import Queue_server

'''
    @param tuple wx_list 公众号列表
    @return RQ
'''
def create_queue(wx_lists=()):
    tmp = []
    if REDIS_FLAG:
        rq = Redis_server()
        rq.init_wx_lists(wx_lists)
    else:
        rq = Queue_server(wx_lists)
    tmp.append(rq)
    tmp.append(REDIS_FLAG)
    return tmp