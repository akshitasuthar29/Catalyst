
from . import views
from django.contrib import admin
from django.urls import path
from allauth.account.views import LogoutView
#from catalyst.views import Upload


urlpatterns = [
    path('', views.home , name='home'),
    path('upload/', views.upload, name="upload"),
    path('query_builder/', views.query_builder, name="query_builder"),
    path('users/',views.users, name="users"),
    path('adduser/',views.adduser, name="adduser"),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    
    

]

