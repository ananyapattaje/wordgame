from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.game_view, name='game'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/daily/', views.daily_report, name='daily_report'),
    path('reports/user/', views.user_report, name='user_report'),
]