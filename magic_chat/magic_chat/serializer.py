from rest_framework import serializers
from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    contact_user_id = serializers.CharField(source="contact.user.user_id")
    contact_phone = serializers.CharField(source="contact.user.phone")
    contact_nickname = serializers.CharField(source="contact.nickname")
    contact_avatar_url = serializers.CharField(source="contact.avatar_url")

    class Meta:
        # 要序列化的 model 是 Contact，把 Contact中的数据序列化成字典结构
        model = Contact

        # 元祖中的值，对应数据「表」中的字段
        # 如果所有字段都要渲染到前端，可以写成 fields = "__all__"
        # 或只选择自己需要的字段
        # 注意：元祖后面必须跟逗号！！
        fields = (
            "contact_user_id",
            "contact_phone",
            "contact_nickname",
            "contact_avatar_url",
            "status"
        )