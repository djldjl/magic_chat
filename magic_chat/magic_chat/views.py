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

from .models import Contact as ModelContact
from .serializer import ContactSerializer
from chat_user.models import CustomUser as ModelUser
from chat_user.models import Profile as ModelProfile   # 下面有IDE标出的红线，没关系，能正常运行


class Contact(APIView):
    authentication_classes = (BasicAuthentication,TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self,request:Request):
        """
        获取联系人
        """
        # 获取本用户的所有联系人
        user_contact = ModelContact.objects.filter(user=request.user,status=ModelContact.STATUS_NORMAL).all()
        # 将数据序列化，即转为类似字典的结构
        user_contact_data = ContactSerializer(user_contact,many=True).data
        context = {
            "data":user_contact_data,
            "status":status.HTTP_200_OK,
            "msg":"获取通讯录成功"
        }
        return Response(context)

    def post(self,request:Request):
        """
        添加联系人；一次添加一个
        """
        contact_phone = request.data.get('phone')
        # user__phone=contact_phone反向查询
        contact_profile = ModelProfile.objects.filter(user__phone=contact_phone).first()
        ModelContact.objects.create(user=request.user,contact=contact_profile)
        context = {
            "status": status.HTTP_200_OK,
            "msg": "添加联系人成功"
        }
        return Response(context)

    def delete(self,request:Request):
        """
        删除联系人;真删除
        """
        contact_phone = request.data.get('phone')
        # contact__user__phone=contact_phone反向查询2次
        ModelContact.objects.filter(user=request.user, contact__user__phone=contact_phone).delete()
        context = {
            "status": status.HTTP_200_OK,
            "msg": "删除联系人成功"
        }
        return Response(context)



