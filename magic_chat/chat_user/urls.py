from django.urls import path, include, re_path
from . import views


urlpatterns = [
    path('register/', views.Register.as_view()),
    path('login/', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),
    path('password/', views.Password.as_view()),
    path('index/', views.Index.as_view()),
    path('profile/', views.Profile.as_view()),
]