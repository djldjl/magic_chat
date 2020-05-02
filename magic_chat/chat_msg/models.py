from django.db import models

from chat_user.models import CustomUser as ModelUser  # 下面有IDE标出的红线，没关系，能正常运行
from chat_user.models import Profile as ModelProfile


class UserChat(models.Model):
    """
    用户会话表；2个人通信即为1个会话，可能对应多条消息；某用户的所有会话对应界面上的消息列表页。
    """
    user_one = models.ForeignKey(ModelUser, related_name="user_one", on_delete=models.CASCADE)
    user_two = models.ForeignKey(ModelUser, related_name="user_two", on_delete=models.CASCADE)
    last_msg = models.CharField(max_length=128, blank=True, null=True)
    # last_msg_time = models.DateTimeField(auto_now=True)
    last_msg_time = models.DateTimeField(blank=True, null=True)
    # 默认为文本类型 0
    msg_type = models.IntegerField(default=0)
    # 默认状态为正常
    status = models.IntegerField(default=1)
    # 默认消息数量为0
    msg_count = models.IntegerField(default=0)
    # 自己添加的，分别记录2个用户的未读消息数
    user1_msg_count = models.IntegerField(default=0)
    user2_msg_count = models.IntegerField(default=0)

    class Meta:
        db_table = "User_chat"
        verbose_name = verbose_name_plural = "用户会话表"

    def __str__(self):
        return str(self.id)


class Message(models.Model):
    """
    消息表
    type:0 文本        1 图片        2 语音        3 视频        100 系统消息
    status:1 正常        2 撤回
    """
    # 这个消息属于哪两个人的消息会话
    chat = models.ForeignKey(UserChat, on_delete=models.CASCADE)
    from_user = models.ForeignKey(ModelUser, related_name="msg_from_user", on_delete=models.CASCADE)
    to_user = models.ForeignKey(ModelUser, related_name="msg_to_user", on_delete=models.CASCADE)
    send_time = models.DateTimeField(auto_now=True)
    message = models.CharField(max_length=255)
    type = models.IntegerField(default=0)
    status = models.IntegerField(default=1)

    class Meta:
        db_table = "message"
        verbose_name = verbose_name_plural = "消息"

    def __str__(self):
        return self.message
