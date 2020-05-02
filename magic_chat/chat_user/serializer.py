from rest_framework import serializers
from .models import Profile


# 使用 serializers 构造一个序列化器,把 model 中的数据转化成类似「字典」的结构

# 1. 序列化功能
# 传入 ORM 模型对象，转为 JSON
# 如果不是用序列化器，要自己把所有数据，一个个从 model 中取出来，再传递

# 2. 反序列功能
# 传入 JSON 数据，自动验证数据 或 保存入库

# 用了模型的序列化器继承 serializers.ModelSerializer

class ProfileSerializer(serializers.ModelSerializer):
    # 查询外键 user 表中的 三个值;字段映射 source=xxx
    # 下面可以引用 profile 表不存在的三个值（位于 Profile 表中的 user 字段中，该字段对应 user 表）
    user_id = serializers.CharField(source="user.user_id")
    phone = serializers.CharField(source="user.phone")
    email = serializers.EmailField(source="user.email")

    # 序列化器使用逻辑是仿照 Django 『表单』设计的
    class Meta:
        # 要序列化的 model 是 profile，把 profile 中的数据序列化成字典结构
        model = Profile

        # 元祖中的值，对应数据「表」中的字段
        # 如果所有字段都要渲染到前端，可以写成 fields = "__all__"
        # 或只选择自己需要的字段
        # 注意：元祖后面必须跟逗号！！
        fields = (
            "user_id",
            "email",
            "phone",
            "nickname",
            "avatar_url",
            "status_text",
        )