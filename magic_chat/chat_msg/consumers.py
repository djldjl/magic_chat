import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.db.models import Q

from chat_user.models import CustomUser as ModelUser
from chat_msg.models import UserChat as ModelUserChat
from chat_msg.models import Message as ModelMessage
from magic_chat.utils import redis


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        """
        Websocket连接。用到了以下参数：
        self.scope
        self.channel_name
        self.channel_layer
        self.channel_layer.group_add
        """
        if self.scope['user'].is_anonymous:
            print('user anonymous')
            self.close()
        self.user = self.scope['user']
        print('user:',self.user.phone)
        # 设置用户在线状态，1为在线；以phone为user_id
        redis.set_user_status(self.user.phone,1)
        # 加入到一个用户组（名字是user.phone）中，以实现每个用户只能收到自己所在用户组的消息
        async_to_sync(self.channel_layer.group_add)(
            self.user.phone,
            self.channel_name
        )
        self.accept()

    def disconnect(self,close_code):
        # 设置用户在线状态，0为离线
        redis.set_user_status(self.user.phone,0)
        # 离开用户组
        async_to_sync(self.channel_layer.group_discard)(
            self.user.phone,
            self.channel_name
        )

    def receive(self, text_data):
        """
        输入的text_data是json格式（类似字典），需要含有message、to_user_id这2个键
        """
        text_data_dict = json.loads(text_data)   # 把json格式数据，转为字典数据
        message = text_data_dict['message']
        to_user_id = text_data_dict['to_user_id']

        # 写入长期数据库的处理；从chat_msg/views中拷过来的，稍作修改
        to_user = ModelUser.objects.filter(phone=to_user_id).first()
        chat = ModelUserChat.objects.filter(Q(user_one=self.user, user_two=to_user)
                                            | Q(user_one=to_user, user_two=self.user)).first()
        if not chat:
            chat = ModelUserChat.objects.create(user_one=self.user, user_two=to_user)
        # 写入message数据库
        msg = ModelMessage.objects.create(chat=chat, from_user=self.user, to_user=to_user, message=message)
        # 更新userchat数据库
        chat.last_msg = message
        chat.last_msg_time = msg.send_time
        chat.msg_count += 1
        chat.save()  # 对象修改值之后要保存，新建的没修改的不用保存
        print("----receive,write in sqlite completed----")

        # 要发送给谁，发到他所在的组里
        channel_name = str(to_user.phone)
        print("channel_name(group):",channel_name)
        async_to_sync(self.channel_layer.group_send)(channel_name,{
            'type':'chat_message',
            'phone':self.user.phone,
            'message':message   # 长连接的时候，尽量让发送的数据小
        })


    def chat_message(self,event):
        # 服务端接收到消息，给 group 中的用户发送一次消息
        message = event['message']
        print('----send----')
        # Send message to WebSocket;json.dumps是把字典转为json格式字符串
        self.send(text_data=json.dumps({'message': message}))
