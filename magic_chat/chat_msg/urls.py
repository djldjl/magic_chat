from django.urls import path, include, re_path
from . import views_v3 as views


urlpatterns = [
    path('list/', views.MsgList.as_view()),
    path('', views.Message.as_view()),
]