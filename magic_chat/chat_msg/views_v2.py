"""
用rest_framework提供的分页功能，实现3种分页方式：PageNumber\offset\Cursor(游标，实现加密)
使用django自带的cache(后台是redis)，实现未读消息数的存储
"""
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination,CursorPagination

from django.core.cache import cache

from .serializer_v2 import MsgListSerializer, MessageSerializer
from chat_user.models import CustomUser as ModelUser
from chat_user.models import Profile as ModelProfile  # 下面有IDE标出的红线，没关系，能正常运行
from .models import UserChat as ModelUserChat
from .models import Message as ModelMessage


class MsgList(APIView):
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        """
        获取消息列表，就是某用户所有的会话
        """
        # 大 Q 就是 or 的意思，分别查询 user_one 和 user_two，找到跟本用户相关的所有会话
        msg_list = ModelUserChat.objects.filter(Q(user_one=request.user) | Q(user_two=request.user)).all()
        # 为了区分会话中的用户（谁是自己，谁是对方），传context，配合serializer_v2使用
        msg_list_data = MsgListSerializer(msg_list,
                                          context={'user_id':request.user.user_id},
                                          many=True).data
        context = {
            "status": status.HTTP_200_OK,
            "msg": "获取会话列表成功",
            "data": msg_list_data,
        }
        return Response(context)


# 自定义PageNumberPagination
class MSGPageNumber(PageNumberPagination):
    page_size = 5  # 默认每页显示多少条，类似 limit
    page_size_query_param = "page_size"  # 通过 URL 参数，改变每页默认显示多少条
    page_query_param = "page"  # 通过 URL 参数，获取页数
    max_page_size = None   # 最大页数限制，None为不限制

    # 改写展示格式
    def get_paginated_response(self, data):
        # 根据官方文档获取的参数
        return Response({
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "count": self.page.paginator.count,
            "page_num": self.page.paginator.num_pages,
            # 把 status 和 msg 提到外面
            "status": data["status"],
            "msg": data["msg"],
            "data": data["data"]
        })

# 自定义LimitOffsetPagination,用limit\offset方式分页
class MSGLimitOffset(LimitOffsetPagination):
    default_limit = 5   # 默认一页几个数据
    limit_query_param = "limit"  # 通过 URL 参数，改变每页默认显示多少条
    offset_query_param = "offset"   # 起始数据的位置，也可看做跳过多少行数据
    max_limit = 100   # 可以改为 None 不限制

# 用游标（加密）的方式分页，隐蔽性很好，看到的上一页、下一页的cursor参数都是一样的；也不显示总共有多少条
class MSGCursorPagination(CursorPagination):
    page_size = 5    # 默认一页几个数据
    cursor_query_param = "cursor"   # 从 url 参数中获取分页 key，作用相当于页码
    ordering = "-send_time"   # 排序规则
    page_size_query_param = "page_size"    # 通过 URL 参数，改变每页默认显示多少条
    max_page_size = None


class Message(APIView):
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        """
        获取某个会话的所有消息
        args:
        user_chat_id # 所属会话
        start_time(可选，查历史消息) # 日期格式："2020-04-26 08:04:52.873571"，可以省去后面的部分，但是格式必须对；
        page # 取哪一页
        page_size # 每页放几条数据
        limit  # 每页放几条数据
        offset  # 起始数据的位置，也可看做跳过多少行数据
        cursor  # 从 url 参数中获取分页 key，作用相当于页码
        page_size
        """
        user_chat_id = request.query_params.get('user_chat_id')
        start_time = request.query_params.get('start_time')

        if not user_chat_id:
            context = {"status": status.HTTP_400_BAD_REQUEST,"msg": "参数不正确，没有给出'user_chat_id'"}
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
        # 只能查看跟本用户相关的会话
        user_chat = ModelUserChat.objects.filter(Q(id=user_chat_id,user_one=request.user)|
                                                 Q(id=user_chat_id,user_two=request.user)).first()
        if not user_chat:
            context = {"status": status.HTTP_400_BAD_REQUEST,"msg": "超范围查数据"}
            return Response(context,status=status.HTTP_400_BAD_REQUEST)
        # 如果有start_time参数，就是查看历史消息，返回start_time之前所有的历史消息；send_time__lt，小于
        if start_time:
            msg = ModelMessage.objects.filter(chat=user_chat,send_time__lt=start_time).all().order_by('-send_time')
        # 如果没有start_time参数，就是查看最新消息；order_by('-send_time')倒序
        else:
            msg = ModelMessage.objects.filter(chat=user_chat).all().order_by('-send_time')
            if user_chat.user_one == request.user:
                user_chat.user1_msg_count = 0
            else:
                user_chat.user2_msg_count = 0
            user_chat.save()
            # 清空缓存中的未读消息数
            cache_key = f"{request.user.user_id}_{str(user_chat.id)}_msg_count"
            cache.set(cache_key,0)

        # 用某种分页器分页展示
        paginator = MSGPageNumber()   # 初始化，不带参数
        msg = paginator.paginate_queryset(msg,   # 对msg进行分页
        # 分页参数从request中获取，包括：可能是page_size和page，或者是offset和limit，或者是cursor和page_size
                                          request=request,
                                          view=self)  # 在本API返回结果

        msg_data = MessageSerializer(msg,many=True).data
        context = {
            "status": status.HTTP_200_OK,
            "msg": "获取该会话的消息成功",
            "data": msg_data,
        }
        # return Response(context)
        # 一般用get_paginated_response返回（Response其实也可以），有自己的封装格式；
        # context在results中,可改写将context内容提上一级
        return paginator.get_paginated_response(context)

    def post(self, request: Request):
        """
        发送消息
        args:to_user_phone,message
        """
        to_user_phone = request.data.get('to_user_phone')
        message = request.data.get('message')
        to_user = ModelUser.objects.filter(phone=to_user_phone).first()
        # 找对应的会话
        chat = ModelUserChat.objects.filter(Q(user_one=request.user, user_two=to_user)
                                            | Q(user_one=to_user, user_two=request.user)).first()
        # 如果user_chat为空，则说明之前没有对应的会话，是第一次通信，需要新建会话
        if not chat:
            chat = ModelUserChat.objects.create(user_one=request.user, user_two=to_user)

        # 构建message对象的元素已凑齐，可以创建message了
        msg = ModelMessage.objects.create(chat=chat, from_user=request.user, to_user=to_user, message=message)

        # 利用缓存存储未读消息数;没发一条消息，就给对方的未读消息数加1
        cache_key = f"{to_user.user_id}_{str(chat.id)}_msg_count"
        msg_count = cache.get(cache_key)
        msg_count = msg_count + 1 if msg_count else 1
        cache.set(cache_key,msg_count)

        # 对相应对话做一些更新
        chat.last_msg = message
        chat.last_msg_time = msg.send_time
        # 对未读消息数量的更新;如果本用户是user_one，则给user2的未读消息数加1
        if chat.user_one == request.user:
            chat.user2_msg_count += 1
        else:
            chat.user1_msg_count += 1
        chat.save()    # 对象修改值之后要保存，新建的没修改的不用保存

        context = {
            "status": status.HTTP_200_OK,
            "msg": "发送消息成功",
        }
        return Response(context)
