from rest_framework import serializers
from .models import UserChat, Message


class MsgListSerializer(serializers.ModelSerializer):
    user_one = serializers.CharField(source="user_one.phone")
    user_two = serializers.CharField(source="user_two.phone")
    last_msg_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S.%f")  # .%f 纳秒

    class Meta:
        # 要序列化的 model 是UserChat
        model = UserChat
        fields = ("id", "user_one", "user_two", "last_msg", "last_msg_time", "msg_type", "msg_count", "status")


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = "__all__"

