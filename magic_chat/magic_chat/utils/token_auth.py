from rest_framework.authtoken.models import Token


class TokenAuthMiddleware:
    """
    Django 不带 Token，我们用第三方库实现的 Token，自己做一次鉴权；针对
    能生效是因为magic_chat/rounting.py里面配置了application的属性："websocket": TokenAuthMiddleware
    Token authorization middleware for Django Channels 2
    ws://127.0.0.1:8000/ws/chat/?token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&aaa=test
    """

    def __init__(self, inner):
        self.inner = inner

    # scope可以看作 websocket 连接的 request
    def __call__(self, scope):
        # 得到一个参数构成的字典
        query = dict((x.split("=") for x in scope["query_string"].decode().split("&")))
        token = query["token"]    # 找到 token文本
        token = Token.objects.get(key=token)  # 生成对应的token，也是在此过程中完成token鉴权
        # 使用时，scope["user"] 获取的 user 直接使用，相当于做了鉴权
        scope["user"] = token.user
        return self.inner(scope)