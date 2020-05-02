from .models import CustomUser as User


class CustomBackend:
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
    """

    def authenticate(self,
                     request,
                     user_id=None,
                     phone=None,
                     password=None,
                     **kwargs):
        # 支持后台登录功能，因为admin登录提交的时候会发送username字段
        if user_id is None:
            user_id = kwargs.get('username')

        try:
            if phone:
                user = User.objects.get(phone=phone)
            elif user_id:
                user = User.objects.get(user_id=user_id)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None