from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter,URLRouter

from magic_chat.utils.token_auth import TokenAuthMiddleware
import chat_msg.rounting


application = ProtocolTypeRouter({
    # 根据鉴权进行修改后的中间件
    "websocket": TokenAuthMiddleware(
        URLRouter(
            chat_msg.rounting.websocket_urlpatterns
        )
    ),
})