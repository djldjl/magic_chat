from django.db import models
from django.core import validators
from django.contrib.auth.models import ( BaseUserManager, AbstractBaseUser)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class CustomUserManager(BaseUserManager):
    def create_user(self, user_id, phone, email=None, password=None):
        """
        Creates and saves a User with the given phone,....
        """
        if not phone:
            raise ValueError('phone must be given when create user')
        if email:
            email = self.normalize_email(email)

        user = self.model(
            user_id = user_id,
            phone = phone,
            email = email,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, phone=None, email=None, password=None):
        user = self.create_user(
            user_id,
            phone=phone,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    user_id = models.CharField(
        max_length=30,
        unique=True,
    )
    phone = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        unique=True,
        default=None,
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return self.user_id

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin   # 是admin的话，就是雇员


class Profile(models.Model):
    """
    用户个人设置
    """
    # 外键 一对一字段，一个用户对应一个配置;第一个参数 被关联的 Model 名称;
    # 第二个参数 CASCADE 级联删除,当 CustomUser 数据表里面的数据被删除后 Profile 里面的数据也随着被删除
    # Profile 类中的 user 字段，其类型是对应 CustomUser 类中的 OneToOneField
    # 如果没有添加关联字段，会自动关联 CustomUser 的主键
    # related_name="user_profile"应该是为了方便反向查找，即知道CustomUser对象查对应的Profile对象
    user = models.OneToOneField(CustomUser,related_name="user_profile",on_delete=models.CASCADE)
    nickname = models.CharField(max_length=191,null=True,blank=True)  # 191 是为了兼容 mysql 的 mp four 方式，最大支持 191
    avatar_url = models.CharField(max_length=191,null=True,blank=True)
    status_text = models.CharField(
        verbose_name="个性签名",
        max_length=10,
        null=True,
        blank=True)

    class Meta:
        db_table = "user_profile"    # 数据库中表名称


