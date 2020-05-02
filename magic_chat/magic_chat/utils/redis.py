"""
websocket时创建；后又实现存储未读消息数
有点疑惑：测试websocket时，额外启动了redis服务，而测试读写未读消息数的时候没有；
后来再次测试websocket，没有启动redis也可以，猜测是django_redis自动启动了一个redis
"""
import redis
from django.conf import settings

# 连接池化，兼容了官方大部分命令
conn = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def get_user_status(user_id):
    """
    查看用户状态
    """
    return conn.hget("user_status", user_id)


def set_user_status(user_id, status):
    """
    设置用户状态
    1 在线
    0 不在线
    """
    return conn.hset("user_status", user_id, status)  # 表名、key、value


def get_user_msg_count(key):
    """
    查看用户未读消息数，key形如：f"{request.user.user_id}_{str(user_chat.id)}_msg_count"
    """
    return conn.get(key)


def set_user_msg_count(key, value=None):
    """
    设置用户未读消息数，处理逻辑是：
    1、有value值，则直接设置msg_count为value值，设为0也可以，通常用来清零；
    2、没有value值，则给原msg_count值加1，原msg_count没有的话就设为1.
    """
    if value or value == 0:
        return conn.set(key, value)
    msg_count = conn.get(key)
    # 拿出来都是 byte 要转成 int
    msg_count = int(msg_count) + 1 if msg_count else 1
    return conn.set(key, msg_count)
