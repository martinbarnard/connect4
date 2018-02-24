from django.conf.urls import url
from django.contrib.auth import login, authenticate
from django.urls import path
from . import views

app_name = 'connect4'

# Play sets up a game which will be visible in the games url
# join will what happens when you join a game.
urlpatterns = [
    path('',        views.IndexView.as_view(), name='games'),
    path('login/',  views.login),
    path('signup/', views.signup),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('games/',  views.GamesView.as_view(), name='games'),
    path('play/<int:pk>',   views.play),
]
