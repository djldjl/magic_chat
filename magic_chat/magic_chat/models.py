from django.db import models
from chat_user.models import CustomUser as User   # 下面有IDE标出的红线，没关系，能正常运行
from chat_user.models import Profile


# 通讯录列表
class Contact(models.Model):
    """
    联系人表
    """
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, "正常"),
        (STATUS_DELETE, "拉黑"),
    )

    # user表示某用户，一个 user 对应多个contact（联系人）
    user = models.ForeignKey(User,
                             # 反向查找别名
                             related_name="contact_user",
                             # 级联删除
                             on_delete=models.CASCADE)

    # 联系人的头像信息等存储在个人配置中
    # 个人配置信息在 profile 表中，不能只映射 user 表
    contact = models.ForeignKey(Profile,
                                related_name="contact",
                                on_delete=models.CASCADE)
    # 状态，假删除就只改这里
    status = models.PositiveIntegerField(default=STATUS_NORMAL,
                                         choices=STATUS_ITEMS,
                                         verbose_name="状态")

    class Meta:
        db_table = "contact"
        verbose_name = "联系人表"

    def __str__(self):
        return self.user