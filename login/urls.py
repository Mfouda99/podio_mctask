from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_start, name='login_start'),
    path('login/oauth/', views.oauth_redirect, name='oauth_redirect'),
    path('login/callback/', views.callback, name='login_callback'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
