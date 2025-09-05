from django.contrib import admin
from django.urls import path
from app1 import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.chess_view, name="chess"),
    path("chess/", views.chess_view, name="chess"),
    path("about/", views.about, name="about"),
    path("history/", views.history, name="history"),
    path("rules/", views.rules, name="rules"),
    path("login/", views.user_login, name="login"),
    path('join/', views.join, name='join'),

    
    path("logout/", views.user_logout, name="logout"),
]
