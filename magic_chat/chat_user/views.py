import uuid
from django.shortcuts import render
from django.contrib import auth
from django.conf import settings
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication,SessionAuthentication,TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny,IsAuthenticated

from .models import CustomUser as User,Profile as ModelProfile
from .serializer import ProfileSerializer


class Register(APIView):
    def post(self, request):
        """
        注册
        """
        phone = request.data.get('phone')
        password = request.data.get('password')
        user_id = uuid.uuid4().hex
        user = User.objects.create_user(user_id=user_id, phone=phone, password=password)
        user.save()
        # 有了用户之后马上新建一个配置文件
        ModelProfile.objects.create(user=user)

        context = {
            "status": status.HTTP_200_OK,
            "msg": "用户注册成功"
        }
        return Response(context)


class Login(APIView):
    authentication_classes = (BasicAuthentication,TokenAuthentication)   # 使用基础的和token的验证方式
    permission_classes = (AllowAny,)    # 允许所有人访问

    def post(self, request):
        """
        登录
        """
        phone = request.data.get('phone')
        password = request.data.get('password')
        user = auth.authenticate(request, phone=phone, password=password)
        if user:
            auth.login(request, user)
            token = Token.objects.create(user=user)
            context = {
                "status": status.HTTP_200_OK,
                "msg": "用户登录成功",
                "user_id":request.user.user_id,
                "token":token.key,
            }
        else:
            context = {
                "status": status.HTTP_403_FORBIDDEN,
                "msg": "用户名或密码错误",
            }
        return Response(context)


class Logout(APIView):
    authentication_classes = (BasicAuthentication,TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        登出
        """
        #auth.logout(request)
        Token.objects.filter(user=request.user).delete()
        context = {
            "status": status.HTTP_200_OK,
            "msg": "退出成功"
        }
        return Response(context)


class Password(APIView):
    authentication_classes = (BasicAuthentication,TokenAuthentication)   # 使用基础的和token的验证方式
    permission_classes = (IsAuthenticated,)     # 只允许所有通过鉴权的人访问

    def post(self, request):
        """
        修改密码
        """
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')
        if new_password1 and new_password1 == new_password2:
            request.user.set_password(new_password1)
            request.user.save()
            context = {
                "status": status.HTTP_200_OK,
                "msg": "修改密码成功"
            }
        else:
            context = {
                "status": status.HTTP_403_FORBIDDEN,
                "msg": "两次密码不一样或没密码"
            }
        return Response(context)


class Index(APIView):
    authentication_classes = (BasicAuthentication,TokenAuthentication)      # 使用基础的和token的验证方式
    permission_classes = (IsAuthenticated,)     # 只允许所有通过鉴权的人访问

    def get(self,request):
        context = {
            "data":"Hello World!",
            "status":200,
            "msg":"访问index成功"
        }
        return Response(context)


class Profile(APIView):
    authentication_classes = (BasicAuthentication,TokenAuthentication)      # 使用基础的和token的验证方式
    permission_classes = (IsAuthenticated,)     # 只允许所有通过鉴权的人访问

    def get(self,request):
        """
        查看用户个人设置
        """
        # 从数据库中拿出「该请求过来的 user」对应的一行配置数据
        user_profile = ModelProfile.objects.filter(user=request.user).first()
        # 序列化方式，把 user_profile 变成类似字典的样式返回
        user_profile_data = ProfileSerializer(user_profile).data

        context = {
            "data":user_profile_data,
            "status":status.HTTP_200_OK,
            "msg":"获取用户设置信息成功"
        }
        return Response(context)

    def put(self,request:Request):
        """
        用户个人设置的修改
        args:
            * nickname
            * avatar_url
            * status_text
        """
        nickname = request.data.get('nickname')
        avatar_url = request.data.get('avatar_url')
        status_text = request.data.get('status_text')
        user_profile = ModelProfile.objects.filter(user=request.user).first()

        if nickname:
            user_profile.nickname = nickname
        if avatar_url:
            user_profile.avatar_url = avatar_url
        if status_text:
            user_profile.status_text = status_text
        user_profile.save()

        # 序列化方式，把 user_profile 变成类似字典的样式返回
        user_profile_data = ProfileSerializer(user_profile).data

        context = {
            "status": status.HTTP_200_OK,
            "msg": "修改用户设置成功",
            "修改后data": user_profile_data,
        }
        return Response(context)


