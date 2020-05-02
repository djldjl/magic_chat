"""
对serializer重构，主要是增加了MsgList的输出，能显示出用户自己和对方用户。
使用自定义的redis连接，实现未读消息数的存储
"""
from rest_framework import serializers
from .models import UserChat, Message
from chat_user.serializer import ProfileSerializer
from django.core.cache import cache
from magic_chat.utils.redis import get_user_msg_count


class MsgListSerializer(serializers.ModelSerializer):
    """
    用到了之前写的ProfileSerializer；
    不仅能显示出用户自己和对方用户，还能显示出每个用户的profile详细信息
    """
    # 根据user找到profile，进而序列化，成为字典
    user_one = ProfileSerializer(source="user_one.user_profile")
    user_two = ProfileSerializer(source="user_two.user_profile")
    last_msg_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S.%f")

    class Meta:
        model = UserChat
        fields = ("id", "user_one", "user_two", "last_msg", "last_msg_time",
                  "msg_count","user1_msg_count", "user2_msg_count", "msg_type", "status")

    # 对 序列化后的结果进行「自定义过滤」
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # print(type(ret))  # OrderedDict

        if ret["user_one"]["user_id"] == self.context.get("user_id"):
            # 之前 只有 user_one 和 user_two，不知道是本用户是谁，现在知道了
            user_info = ret.pop("user_one")
            to_user_info = ret.pop("user_two")
            ret["user_info"] = user_info  # 本用户
            ret["to_user_info"] = to_user_info   # 对方用户
            # 自己添加的，显示本用户的和对方用户的未读消息数：
            ret["self_msg_count"] = ret.pop("user1_msg_count")
            ret["to_user_msg_count"] = ret.pop("user2_msg_count")
        else:
            user_info = ret.pop("user_two")
            to_user_info = ret.pop("user_one")
            ret["user_info"] = user_info
            ret["to_user_info"] = to_user_info
            ret["self_msg_count"] = ret.pop("user2_msg_count")
            ret["to_user_msg_count"] = ret.pop("user1_msg_count")
        cache_key = f"{self.context.get('user_id')}_{str(ret['id'])}_msg_count"
        ret["cache_msg_count"] = get_user_msg_count(cache_key)
        return ret


class MessageSerializer(serializers.ModelSerializer):
    send_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S.%f")   # 时间显示的格式化

    class Meta:
        model = Message
        fields = "__all__"

