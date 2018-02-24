from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.template import loader
from django.urls import reverse
from django.views import generic

from .models import Game, Coin


def login(request):
    pass

    
def signup(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('games')
    else:
        form = UserCreationForm()
    return render(request, 'connect4/signup.html' , {'form':form})


class IndexView(generic.ListView):
    template_name='connect4/index.html'
    context_object_name='latest_games_list'
    queryset = Game.active_games
    model = Game
    # Override to get our active games
    def get_queryset(self, querytype='actives'):
        '''return the last n-games'''
        if querytype == 'actives':
            return Game.objects.filter(player1==user)
        elif querytype == 'mine':
            return Game.objects.filter(player1==user)
    def get_context_data(self, **kwargs):
        '''
        Override our context data to pass back my last-n games
        '''
        context = super(IndexView, self).get_context_data(**kwargs)
        # build our data
        context['my_actives'] = {}
        context['my_last_n'] = {}
        return context


class LogoutView(generic.DetailView):
    model=Game
    template_name = 'connect4/detail.html'


class GamesView(generic.ListView):
    template_name='connect4/index.html'
    context_object_name='latest_games_list'
    model=Game
    def get_queryset(self):
        '''return the last n-games'''
        return Game.objects.order_by('-created_date')[:10] 

def join_game(request, game_id):
    '''
    '''
    # If there is a game_id and it's in status 'pending', then we'll add this dood to the 
    # game and redirect
    gg = Game.objects.filter(pk==game_id)
    if gg and gg.status == 'pending':
        gg.join_up(request.user)
    return redirect('play', game_id)

def play(request, game_id):
    """
    """
    template_name='connect4/game.html'
    # Create a new game object and then control it with ajax
    return render(request, template_name)

